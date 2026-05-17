#!/usr/bin/env python3
"""Parser for WITandWISDOM joke emails (richardw@olypen.com)."""

"""
# PARSER GUIDELINES (DO NOT DELETE)

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [ ] Use other format
- [x] return empty list (e.g. `[]`)

- How many jokes are expected?
- [ ] Only one
- [x] Specific number: 2
- [ ] Multiple, but no specific number

- Expression to match this parser: `"richardw@olypen.com" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title

- The first start marker is `~~~~~~~ THIS & THAT:` and the second start marker is `~~~~~~~ KEEP SMILING:`. There will always be exactly two jokes.

- [ ] Yes include the start marker in the joke
- [x] No don't include the start marker in the joke

- [x] The rest of the text is the joke text, until you see the end marker.

- The end marker is a line that starts with `~~~~~~~`. The end marker and the start marker of the second joke will most likely be the same line. Since there will always be only two jokes, when you see the second end marker, ignore the remainder of the email.

- [ ] Yes include the end marker in the joke
- [x] No don't include the end marker in the joke

- Are the paragraphs line wrapped, or one long line?
- [x] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [ ] No - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line
"""

import logging

from .email_data import EmailData, JokeData
from . import register_parser

_START_MARKER_1 = "~~~~~~~ THIS & THAT:"
_START_MARKER_2 = "~~~~~~~ KEEP SMILING:"
_END_PREFIX = "~~~~~~~"


def _can_be_parsed_here(email_data: EmailData) -> bool:
  """Return True if this parser can parse the email."""
  return "richardw@olypen.com" in email_data.from_header.lower()


def _extract_joke(lines, start_idx):
  """Extract joke content starting at start_idx, stopping at the next end marker.

  Returns (title, raw_lines, end_idx) where end_idx is the index of the
  end-marker line (or len(lines) if no end marker is found).
  """
  i = start_idx
  title = ""
  title_found = False
  raw_lines = []

  while i < len(lines):
    line = lines[i]

    if line.startswith(_END_PREFIX):
      return title, raw_lines, i

    if not title_found:
      if not line.strip():
        i += 1
        continue
      # First non-blank line: title if ≤35 chars, else first line of joke
      stripped = line.strip()
      title_found = True
      if len(stripped) <= 35:
        title = stripped.title()
      else:
        title = ""
        raw_lines.append(line)
    else:
      raw_lines.append(line)

    i += 1

  return title, raw_lines, i


def _fold_lines(raw_lines):
  """Fold line-wrapped text into paragraphs separated by blank lines.

  Consecutive non-blank lines are joined with spaces. Multiple blank lines
  between paragraphs are collapsed to one.
  """
  paragraphs = []
  current_para = []

  for line in raw_lines:
    stripped = line.strip()
    if stripped:
      current_para.append(stripped)
    else:
      if current_para:
        paragraphs.append(" ".join(current_para))
        current_para = []

  if current_para:
    paragraphs.append(" ".join(current_para))

  return "\n\n".join(paragraphs)


@register_parser(_can_be_parsed_here)
def parse(email_data: EmailData) -> list[JokeData]:
  """Parse WITandWISDOM email and return the two extracted jokes."""
  content = email_data.text
  if not content.strip():
    return []

  lines = content.split("\n")
  jokes = []
  joke_submitter = email_data.from_header
  jokes_found = 0
  i = 0

  while i < len(lines) and jokes_found < 2:
    line = lines[i]

    if jokes_found == 0 and line.startswith(_START_MARKER_1):
      i += 1
      title, raw_lines, end_idx = _extract_joke(lines, i)
      joke_text = _fold_lines(raw_lines).strip()
      if joke_text:
        jokes.append(JokeData(text=joke_text, submitter=joke_submitter, title=title))
        jokes_found += 1
      else:
        logging.warning("WITandWISDOM: empty joke 1 body")
      i = end_idx  # points at the end-marker line (likely _START_MARKER_2)

    elif jokes_found == 1 and line.startswith(_START_MARKER_2):
      i += 1
      title, raw_lines, end_idx = _extract_joke(lines, i)
      joke_text = _fold_lines(raw_lines).strip()
      if joke_text:
        jokes.append(JokeData(text=joke_text, submitter=joke_submitter, title=title))
        jokes_found += 1
      else:
        logging.warning("WITandWISDOM: empty joke 2 body")
      break

    else:
      i += 1

  return jokes
