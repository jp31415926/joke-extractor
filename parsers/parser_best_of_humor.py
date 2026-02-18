"""Parser for Best of Humor emails."""

from .email_data import EmailData, JokeData
from . import register_parser
import logging


def _can_be_parsed_here(email: EmailData) -> bool:
  return "shawn@bestofhumor.com" in email.from_header.lower()


def _is_soj(line: str) -> bool:
  """Return True if line is a Start-of-Joke (SOJ) marker."""
  s = line.strip()
  return (
    (s.startswith('+--') and s.endswith('--+')) or
    (s.startswith('++-') and s.endswith('-++')) or
    s.endswith('<<<') or
    s.startswith('------------------------------')
  )


def _is_eof(line: str) -> bool:
  """Return True if line is an End-of-File (EOF) marker."""
  s = line.strip()
  return s.startswith('~~~~~') or s.startswith('_____') or s == '---'


def _build_joke_text(raw_lines: list[str]) -> str:
  """
  Join consecutive non-blank lines into single-line paragraphs.
  Preserve blank lines between paragraphs.
  Reduce multiple consecutive blank lines to one.
  """
  parts = []
  current_para: list[str] = []

  for line in raw_lines:
    if line.strip():
      current_para.append(line.rstrip())
    else:
      if current_para:
        parts.append(' '.join(current_para))
        current_para = []
      parts.append('')

  if current_para:
    parts.append(' '.join(current_para))

  result: list[str] = []
  prev_blank = False
  for part in parts:
    if part == '':
      if result and not prev_blank:
        result.append('')
      prev_blank = True
    else:
      result.append(part)
      prev_blank = False

  return '\n'.join(result).strip()


def _collect_joke(joke_lines: list[str], jokes: list[JokeData], submitter: str) -> None:
  """Build joke text from raw lines and append to jokes if it passes filters."""
  if not joke_lines:
    return
  joke_text = _build_joke_text(joke_lines)
  if not joke_text:
    return
  lower = joke_text.lower()
  if 'http' in lower or 'mailto' in lower or 'copyright' in lower:
    return
  jokes.append(JokeData(text=joke_text, submitter=submitter, title=''))


@register_parser(_can_be_parsed_here)
def parse(email: EmailData) -> list[JokeData]:
  """
  Parse 'Best of Humor' email format.

  Jokes are delimited by SOJ marker lines:
    - starts with '+--' and ends with '--+'
    - starts with '++-' and ends with '-++'
    - starts with '>>>' and ends with '<<<'

  Processing stops at EOF markers (starts with '~~~~~' or '_____', or equals '---').
  Jokes containing 'http', 'mailto', or 'copyright' are discarded.

  Parameters
  ----------
  email : EmailData
      Email to parse

  Returns
  -------
  list[JokeData]
      List of extracted jokes.
  """
  if not email.text.strip():
    return []

  jokes: list[JokeData] = []
  submitter = email.from_header
  lines = email.text.split('\n')

  in_joke = False
  joke_lines: list[str] = []
  first_nonblank_seen = False

  for line in lines:
    logging.debug(f"line: {line}")
    if _is_eof(line):
      logging.debug('EOJ')
      if in_joke:
        _collect_joke(joke_lines, jokes, submitter)
      break

    if _is_soj(line):
      logging.debug('SOJ')
      if in_joke:
        _collect_joke(joke_lines, jokes, submitter)
      in_joke = True
      joke_lines = []
      first_nonblank_seen = False
      continue

    if in_joke:
      lower = line.strip().lower()
      if not first_nonblank_seen and lower:
        first_nonblank_seen = True
        if 'http' in lower:
          logging.debug("discard beginning 'http'")
          continue  # discard first line if it contains a URL
      if ('bestofhumor.com' in lower or 'free t-shirt' in lower) and \
          not ('http' in lower or 'mailto' in lower or 'copyright' in lower):
        continue # discard any line if it contains 'bestofhumor.com' or 'free t-shirt'
      joke_lines.append(line)
  else:
    # Loop exhausted without hitting an EOF marker
    if in_joke:
      _collect_joke(joke_lines, jokes, submitter)

  return jokes
