# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Joke Extractor** - a Python 3.11+ pipeline that processes joke newsletter emails (`.eml` files) and extracts joke content into structured text files. It has two main layers:

1. **`joke-extract.py`** - The primary script. Takes two output directories + one or more `.eml` files, selects a matching parser from `parsers/`, and writes extracted jokes to the success dir (or the raw email dump to the failure dir).
2. **`parsers/`** - A plugin system where each parser handles a specific joke newsletter sender.

## Commands

### Run the extractor
```bash
python3 joke-extract.py <success_output_dir> <failure_output_dir> <email.eml> [...]
```

### Run unit tests
```bash
python3 -m pytest tests/
python3 -m pytest tests/test_foo.py::test_bar -v   # single test
```

### Clean up output files
```bash
python3 clean_up.py   # deletes all output files, temp files, and jokes/ directory contents
```

## Architecture

### Primary Script (`joke-extract.py`)
- Accepts CLI args: `<success_dir> <failure_dir> <eml_path> [...]` (one or more email files)
- Parses the email with `email.message_from_file()` using ISO-8859-1 encoding
- Extracts `text/plain` - `text_content` (cleaned via `cleanup_body`)
- Extracts `text/html` - `html_content` (converted to plain text via `lynx -dump`, then cleaned)
- Builds an `EmailData` named tuple, finds a matching parser via `get_parser()`, and calls it
- On success: writes each `JokeData` to a `joke_*.txt` tempfile in `<success_dir>`
- On failure (no jokes): dumps raw email data to `email_*.json` and `email_*.txt` in `<failure_dir>`
- Output codes on stdout: `100` = success, `200` = no content, `201` = no joke found, `500-502` = errors

### Parser System (`parsers/`)
- **`email_data.py`** defines the two shared types:
  - `EmailData(text, html, from_header, subject_header)` - immutable input to parsers
  - `JokeData(text, submitter, title)` - immutable output from parsers
- **`__init__.py`** auto-discovers and imports all non-private modules in `parsers/` at load time; parsers self-register via the `@register_parser(_can_be_parsed_here)` decorator
- Each parser file must implement exactly two functions:
  - `_can_be_parsed_here(email: EmailData) -> bool` - matches on `from_header` or `subject_header` only (no content inspection)
  - `parse(email: EmailData) -> list[JokeData]` - decorated with `@register_parser(_can_be_parsed_here)`
- Parser lookup: `get_parser(email)` iterates the registry and returns the first match

### Parser Implementation Rules
- Use `email.html` first (already lynx-converted); fall back to `email.text` only if `email.html` is empty
- Never do your own HTML-to-text conversion
- Return `[]` silently on parse failure - no exceptions, no INFO logging inside parsers
- All parsers are pure functions - no global state, no side effects
- See `parsers/parser-spec3.md` for the full parser spec and `parsers/parser-interface.md` for the interface contract

### Email Sources (`emails/`)
Each subdirectory under `emails/` corresponds to a specific newsletter sender and contains:
- Sample email data as JSON (for developing/testing parsers)
- A `parser-hints.md` describing the parsing logic for that sender

### Test Fixtures (`tests/`)
Unit test `.eml` files covering edge cases: `plain_text.eml`, `html_only.eml`, `empty_text.eml`, `no_text.eml`, `missing_from.eml`, `invalid_attachment.eml`

## Code Style
- Python 3.11+, 2-space indentation, max 88 chars per line, no trailing whitespace
- All scripts must have a `#!/usr/bin/env python3` shebang
- ISO-8859-1 encoding for reading email files (not UTF-8)
- All logging via the `logging` module; stdout is reserved for the `NNN message` result codes
- Standard library only: `sys`, `os`, `email`, `tempfile`, `logging`, `subprocess`, `argparse`
- `lynx` must be installed on the system for HTML conversion
- Double blank lines between top-level function/class definitions; single blank lines between logical sections

### Naming
- Variables/functions: `snake_case` - Classes: `PascalCase` - Constants: `UPPER_CASE` - Private methods: `_snake_case`

### Import order
1. Standard library
2. Third-party
3. Local application (`from .email_data import ...`)
