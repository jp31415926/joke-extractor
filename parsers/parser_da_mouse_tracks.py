"""Parser for Da Mouse Tracks emails."""

"""
# PARSER GUIDELINES (DO NOT DELETE)

- [ ] Text format is preferred
- [x] HTML format is preferred

- What to do if preferred format is empty?
- [x] Use other format
- [ ] return empty list (e.g. `[]`)

- How many jokes are expected?
- [ ] Only one
- [ ] Specific number:
- [x] Multiple, but no specific number

- Expression to match this parser: `"DaMouseTracks-noreply@yahoogroups.com" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title

- The the start of joke marker (SOJ) is a line that 
  - a line that contains at least 10 of the same character in a row.
  - Examples: vvvvvvvvvvvvvvvvvvv or ------------------

- [x] The rest of the text is the joke text, until you see the end of joke marker (EOJ).

- The EOJ also marks the start of the next joke.

- The end of file marker (EOF) is a line that
  - a line that contains at least 10 of the same character in a row.
  - Examples: vvvvvvvvvvvvvvvvvvv or ------------------

- If you reach the last line, discard what you have collected.
- If you reach a line that contains `Today's Recipes`, discard the rest of the email.

- [ ] Yes include the markers in the joke
- [x] No don't include the markers in the joke

- Are the paragraphs line wrapped, or one long line?
- [ ] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [n] No - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line

## Additional Info
Follow these rules in this order:
- If a joke contains the following strings (case insensitive) on any line in the joke, the entire joke should be discarded:
  - `http`
  - `mailto`
  - `Copyright`
  - `Today's Pics`
  - `Today's Links`
  - `Today's Riddle`
  - `Today's Word`

"""
import logging
import re

from .email_data import EmailData, JokeData
from . import register_parser


def _can_be_parsed_here(email: EmailData) -> bool:
  return "damousetracks-noreply@yahoogroups.com" in email.from_header.lower()


def _is_separator(line: str) -> bool:
  """Return True if line contains 10+ consecutive identical characters."""
  return bool(re.search(r'(.)\1{9,}', line.strip()))


_DISCARD_KEYWORDS = (
  'http', 'mailto', 'copyright',
  "today's pics", "today's links", "today's riddle", "today's word",
)


def _build_joke_text(raw_lines: list[str]) -> str:
  """
  Format joke text for HTML source: each non-blank line is its own paragraph,
  separated by blank lines. Existing blank lines in input are ignored.
  """
  parts = []
  for line in raw_lines:
    if line.strip():
      parts.append(line.rstrip())
      parts.append('')
  while parts and not parts[-1]:
    parts.pop()
  return '\n'.join(parts)


_MIN_SINGLE_LINE_LEN = 35


def _collect_joke(
  joke_lines: list[str], jokes: list[JokeData], submitter: str
) -> None:
  if not joke_lines:
    return
  joined_lower = '\n'.join(joke_lines).lower()
  if any(kw in joined_lower for kw in _DISCARD_KEYWORDS):
    return
  joke_text = _build_joke_text(joke_lines)
  if not joke_text:
    return
  if '\n' not in joke_text and len(joke_text) < _MIN_SINGLE_LINE_LEN:
    return
  jokes.append(JokeData(text=joke_text, submitter=submitter, title=''))


@register_parser(_can_be_parsed_here)
def parse(email: EmailData) -> list[JokeData]:
  content = email.html if email.html.strip() else email.text
  if not content.strip():
    return []

  lines = content.split('\n')
  jokes: list[JokeData] = []
  submitter = email.from_header

  collecting = False
  good_morning_seen = False
  joke_lines: list[str] = []

  for line in lines:
    stripped = line.strip()

    if not collecting:
      if stripped == 'Good Morning':
        good_morning_seen = True
        continue
      if good_morning_seen and stripped.startswith('http'):
        collecting = True
      continue

    if "today's recipes" in stripped.lower():
      break

    if _is_separator(line):
      _collect_joke(joke_lines, jokes, submitter)
      joke_lines = []
    else:
      joke_lines.append(line)

  # Reaching end of input: discard whatever was being collected
  return jokes
