"""Parser for 'You Make Me Laugh' (CrosswalkMail) format."""

from . import register_parser

def _is_crosswalk_mail(from_header: str) -> bool:
    return "Crosswalk@crosswalkmail.com" in from_header

@register_parser(_is_crosswalk_mail)
def parse_You_Make_Me_Laugh(text: list, subject: str) -> tuple:
    """
    Parse the "You Make Me Laugh" email format.

    This parser expects a subject like "Acts 2:38 - August 26, 2010", extracts the scripture reference,
    and isolates the joke content between a visual separator line (`__________`) and the footer marker
    `cybersalt.org/cleanlaugh`.

    Parameters
    ----------
    text : list of str
        List containing a single string of the email's text/plain content.
        (Index 0 is used for processing.)
    subject : str
        Original email subject line, expected to contain scripture reference + date.

    Returns
    -------
    tuple
        - list[str]: List with a single cleaned joke content string.
        - str: Cleaned subject (e.g., "Acts 2:38", without the date portion).
    """
    # Extract subject without date (e.g., "Acts 2:38 - August 26, 2010" → "Acts 2:38")
    sub_parts = subject.split('-')
    subject = ''.join(sub_parts[:-1]).strip()

    # Start with full text block in a list (standard for downstream)
    msg = [text[0]]

    lines = text[0].split('\n')

    # Find visual separator line: starts with "__________" (10 underscores)
    bar_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith('__________'):
            bar_index = i
            break

    if bar_index is None:
        return msg, subject

    # Skip 2 lines after the bar
    i = bar_index + 2
    if i >= len(lines):
        return msg, subject

    # Skip "Newsletters" line and next blank line if present
    line_parts = lines[i].split()
    if line_parts and line_parts[-1] == "Newsletters":
        i += 2
        if i >= len(lines):
            return msg, subject

    # Skip the line matching cleaned subject (if present)
    line = lines[i].strip()
    if line == subject:
        i += 1
        if i >= len(lines):
            return msg, subject
        line = lines[i].strip()

    # Collect content until reaching footer marker
    new_content = ""
    while i < len(lines) and line != "cybersalt.org/cleanlaugh":
        new_content += line + "\n\n"
        i += 1
        if i < len(lines):
            line = lines[i].strip()
        else:
            line = ""

    if new_content:
        msg[0] = new_content

    return msg, subject
