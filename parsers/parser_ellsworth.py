"""Parser for Thomas S. Ellsworth emails — extract jokes from Good Clean Fun emails."""

from .email_data import EmailData, JokeData
from . import register_parser
import logging

logging.basicConfig(level=logging.WARNING)

def _can_be_parsed_here(email: EmailData) -> bool:
    """Return True if this parser can parse the email."""
    return "tellswor@kcbx.net" in email.from_header.lower()


@register_parser(_can_be_parsed_here)
def parse(email: EmailData) -> list[JokeData]:
    """Parse email and return a list of extracted jokes (one per email, max)."""
    jokes = []
    submitter = email.from_header

    # Prefer text (as per hints: "Text format is the only format available")
    lines = email.text.split('\n') if email.text.strip() else []

    # Find start delimiter: line that starts with "----------" (exactly 10 dashes)
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("----------"):
            start_idx = i
            break

    if start_idx == -1:
        return []  # No start delimiter → return empty list

    # Get subject for title (from hints: "Use email.subject_header as the title. Remove the prefix 'GCF: '.")
    raw_subject = email.subject_header or ""
    if raw_subject.startswith("GCF: "):
        title = raw_subject[5:]  # Remove "GCF: " prefix
    else:
        title = raw_subject

    # Next line after start delimiter should be the repeated subject line ("GCF: ...")
    # Skip it if it matches the subject (or its "GCF: " version) exactly
    next_line_idx = start_idx + 1
    next_line = lines[next_line_idx].strip() if next_line_idx < len(lines) else ""

    # Normalize for comparison: strip prefix, strip whitespace
    expected_subject_line = "GCF: " + title if title else ""
    # Also compare to raw subject line (which may have trailing spaces, etc.)
    if next_line in [expected_subject_line, raw_subject]:
        # Skip this line (don't include in joke text)
        start_idx = next_line_idx

    # Now collect lines until end delimiter (another "----------")
    joke_lines = []
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.startswith("----------"):
            end_idx = i
            break
        # Include non-empty lines (keep blank lines between non-blank lines)
        joke_lines.append(line)

    # Join joke text: join non-empty lines with '\n\n'
    # But preserve internal blank lines → replace consecutive blanks with single blank, but keep structure
    # More precisely: join with '\n\n' only between non-empty lines
    cleaned_lines = []
    for line in joke_lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)

    # Join with '\n\n'
    joke_text = '\n\n'.join(cleaned_lines).strip() if cleaned_lines else ""

    # If we found a joke, create JokeData
    if joke_text:
        jokes.append(JokeData(
            text=joke_text,
            submitter=submitter,
            title=title
        ))

    return jokes
