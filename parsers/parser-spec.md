# Parser Specification (`parser-spec.md`)

> **Version**: 1.0  
> **Purpose**: Developer-ready specification for implementing a new email joke parser.  
> **Prerequisites**: See `parser-interface.md` and `email_data.py`.  
> **Key Principle**: *Parse deterministically, reject silently, log only for debug.*

---

## 1. Core Interface (Mandatory)

All parsers **must** implement the following two functions with *exact* signatures:

```python
def _can_be_parsed_here(email: EmailData) -> bool:
    """Return True if this parser can parse the email."""
    ...

def parse(email: EmailData) -> list[JokeData]:
    """Parse email and return a list of extracted jokes (possibly empty)."""
    ...
```

- **No optional arguments** or kwargs.
- **No mutation** of `email` (see §3).
- Use `from .email_data import EmailData, JokeData` (or relative import consistent with project layout).
- Register parser automatically via `from . import register_parser` (see §2.3).

---

## 2. Parser Implementation Rules

### 2.1. Email Selection (`_can_be_parsed_here`)
- **Only use `email.from_header` and/or `email.subject_header`** for identification.
- **Avoid brittle patterns** (e.g., exact substrings like `"Bestofhumor.com"` instead of `"bestofhumor.com"`).
  - Prefer case-insensitive checks (`"example.com" in email.from_header.lower()`).
- **Do not parse content** to determine eligibility — that belongs in `parse()`.
- **Return `False` early** if identification fails — no side effects.

> ✅ Good: `"@sandersonmail.org" in email.from_header.lower()`  
> ❌ Bad: `if "funny" in email.subject_header: return True`

### 2.2. Content Parsing (`parse`)
#### Input Source Precedence (defaults if `hints.txt` is silent)
| Scenario | Action |
|----------|--------|
| `email.html` non-empty | **Use HTML content** (preferred) |
| `email.html` empty/whitespace | Fall back to `email.text` |
| Both empty | Return `[]` |

#### HTML Handling
- HTML content is provided *as-is* — parsers may:
  - Split on `\n` and process raw HTML lines (as in existing parsers), **or**
  - Use `html.parser`/`BeautifulSoup` if external libs are allowed and needed.
- **No validation** of HTML correctness is required (per your instruction: *"I don't care"* about malformed HTML).

#### Joke Extraction Rules (standard conventions)
- Return a `list[JokeData]` — **empty list if no jokes found** (even on parse error).
- **Do not crash** on malformed/missing data.
- Each joke must include:
  - `text`: Stripped joke body (no trailing newlines, spaces).
  - `submitter`: Full raw `from_header` (e.g., `"Shawn <shawn@host.com>"`).
  - `title`: Extracted subject (may be `""` if none).

> 📌 **Title extraction**: Always document logic in `hints.txt`. Defaults:
> - If a title line exists (e.g., line after `"HUMOR"` ≤35 chars), use `.title()` for normalization.
> - If no title exists → `title = ""`.

### 2.3. Logging & Error Handling
- **Use Python’s `logging` module** (as in `parser_sanderson.py`):
  ```python
  import logging
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
  ```
- **Log at `WARNING` or `ERROR` only** — e.g., unexpected structure, duplicate jokes, or skipped content.
- **Never log at `INFO` in production** — `_can_be_parsed_here` and `parse` run for *every* email.
- **Silently skip invalid input**:
  - If `"HUMOR"` marker missing → return `[]` (not `raise`).
  - If end delimiter (`<>< `) missing → extract to end of email, but log `WARNING`.

### 2.4. External Libraries
- **Allowed**: Standard library (`re`, `html.parser`, `json`) and *optional* libraries (e.g., `beautifulsoup4`, `html2text`) **if needed**.
- **Preferred**: Use stdlib-first. Add `requirements.txt` update *only* if external lib is critical.
- Comment imports: `# Optional: pip install beautifulsoup4` if non-stdlib.

---

## 3. Data Contract & Safety

| Field | Mutability | Notes |
|-------|------------|-------|
| `EmailData` | Immutable | `tuple` — parsers may **only read** |
| `JokeData` | Immutable | Parsers return new `JokeData()` instances |
| `joke_submitter` | Must be raw `from_header` | Never sanitize (e.g., don’t extract email only) |
| `joke_text` | Must be normalized | Strip leading/trailing whitespace; preserve internal `\n\n` spacing |

---

## 4. Hints File Format (for `hints.txt`)

Every parser *must* have an accompanying `hints.txt`. It must include **all** of the following:

```markdown
# hints.txt for [Parser Name]

## Identification
- Used in `_can_be_parsed_here()`
- Pattern to match: "exact substring or regex pattern" (case-insensitive if needed)
- Example: `"GrampsTN@comcast.net" in email.from_header.lower()`

## Parsing Logic
- Content source preference: `html` / `text` / `auto` (default: `html`)
- Start delimiter: `"HUMOR"` (first line must *start with* this, e.g., `line.startswith("HUMOR")`)
- End delimiter: `"<>< "` (stop before lines *starting with* this)
- Title extraction rule: 
  - Rule: "Next non-blank line ≤35 chars (length includes spaces)"
  - Case normalization: `title.title()` (or none)
  - Fallback if missing: `title = ""`
- Whitespace rules: 
  - Skip blank lines? `True/False`
  - Join lines with `\n\n`? `True` (recommended)
  - Preserve `\r`? `False` (strip CR on read)

## Edge Cases
- If no start delimiter found → return `[]`
- If end delimiter missing → extract to EOF, log `WARNING`
- If multiple jokes per email? `Yes/No` (default: `Yes`)
- Submitter handling: Always use `email.from_header` (never derive from body)
```

> 🔔 **Note**: `hints.txt` is for *human readers* — the parser implementation must *not* parse this file. It’s guidance only.

---

## 5. Architecture & Integration

### 5.1. Parser Discovery & Registration
- All parsers reside in `parsers/` directory (e.g., `parsers/parser_christian_voices.py`).
- Each parser **registers itself** via:
  ```python
  from . import register_parser

  def _can_be_parsed_here(...) -> bool: ...
  @register_parser(_can_be_parsed_here)
  def parse(...) -> list[JokeData]: ...
  ```
- `register_parser()` (in `parsers/__init__.py`) stores parsers in a global registry (e.g., `PARSERS: list[tuple[Callable, Callable]]`), sorted by specificity.

### 5.2. Execution Pipeline
1. For each incoming `EmailData`:
   - Iterate registered parsers in order (most specific first).
   - Call `_can_be_parsed_here()` — first `True` wins.
   - Call `parse()` on winner → collect `list[JokeData]`.
2. If no parser matches → `[]` (no error).
3. No global state (parsers must be stateless).

---

## 6. Testing Plan

### Unit Tests (per parser)
- **Minimum 3 tests** per parser:
  1. `_can_be_parsed_here()` matches correct `from_header`/`subject_header`.
  2. `parse()` returns `list[JokeData]` for valid email.
  3. `parse()` returns `[]` for email without joke (e.g., missing `"HUMOR"`).
- **Include edge cases**:
  - Empty email body → `[]`
  - Title line = 35 chars → use it; 36 chars → `title = ""`
  - Delimiter at start/end → handle gracefully.

### Test Data Format
Provide JSON files in `tests/fixtures/`:
```json
{
  "subject": "Sample Subject",
  "from": "\"Sender\" <sender@example.com>",
  "plain_text": "HUMOR\nTitle\nJoke text\n<>< \nFooter",
  "html_text": "<p>HUMOR<br>Title<br>Joke text<br><>< <br>Footer</p>"
}
```
- Use `email_data.EmailData(**json_data)` to construct test input.

### Coverage Checklist
- [ ] All delimiters matched exactly (start/end)
- [ ] Title extraction (length, normalization)
- [ ] Whitespace normalization (`\n\n` between lines)
- [ ] Empty/missing data → no crash, `[]` return
- [ ] HTML vs. text fallback (when specified in `hints.txt`)
- [ ] Logging (only warnings/errors)

---

## 7. Example Parser Skeleton

```python
"""Parser for [Parser Name] — see hints.txt for details."""

from .email_data import EmailData, JokeData
from . import register_parser
import logging

logging.basicConfig(level=logging.WARNING)

def _can_be_parsed_here(email: EmailData) -> bool:
    # Implement per hints.txt
    return "example.com" in email.from_header.lower()

@register_parser(_can_be_parsed_here)
def parse(email: EmailData) -> list[JokeData]:
    jokes = []
    joke_submitter = email.from_header
    lines = []
    if email.html.strip():
        lines = email.html.split('\n')
    else:
        lines = email.text.split('\n')

    # State machine / loop as per hints.txt
    # ...
    return jokes
```
