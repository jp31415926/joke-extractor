#!/usr/bin/env python3
"""
Script to extract joke content from email files, supporting multiple joke email formats.
Supports parsing:
- "You Make Me Laugh" emails (CrosswalkMail)
- Steve Sanderson's "Sunday Fun Stuff" emails
Prioritizes `text/plain` over `text/html`, and cleans up content before output.

Usage:
    python 01-extract-text.py <email_file> <output_directory>
"""

import sys
import os
import email
import tempfile
import logging
import subprocess

# Configure logging to stderr for visibility in pipelines
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


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


def parse_Sanderson(text: list) -> tuple:
    """
    Parse Steve Sanderson's "Sunday Fun Stuff" email format.

    This parser identifies jokes delimited by:
    - Start marker: `*` repeated ≥10 times (`**********`)
    - Title: a line ending with `:`
    - Joke body: lines up until the next `[...]:`-style closing tag (e.g., `[end]`)
    - Ends at a line containing exactly `Steve Sanderson`

    Parameters
    ----------
    text : list of str
        List containing a single string of the email's text/plain content.
    subject : str
        Subject line — unused because Sanderson email Subjects don't describe the jokes themselves

    Returns
    -------
    tuple
        - list[str]: List of extracted joke bodies.
        - str: From header
    """
    # Sanderson email Subjects don't describe the jokes themselves.
    # Someone (or an AI?) will have to come up with subjects later.
    from_hdr = "Steve C Sanderson <aardvark@illinois.edu>"

    jokes = []
    i = 0
    state = 0
    new_content = ""

    lines = text[0].split('\n')

    # State machine for parsing:
    # 0: wait for "*..." line (start of joke block)
    # 1: skip blank lines, then expect title (ends with ':')
    # 2: skip blank line before joke body
    # 3: collect lines until closing tag (e.g., `[end]`)
    while i < len(lines):
        line = lines[i].strip()

        match state:
            case 0:  # Wait for start delimiter
                if line.startswith('*' * 10):  # e.g., "**********"
                    state = 1
                i += 1

            case 1:  # Find title (line ending with ':')
                if not line:
                    i += 1
                elif line.endswith(':'):
                    state = 2
                    i += 1
                elif line == 'Steve Sanderson':
                    # End of content
                    i = len(lines)
                else:
                    # No title — jump to content (non-standard)
                    state = 3

            case 2:  # Skip blank line before joke body
                if not line:
                    i += 1
                state = 3

            case 3:  # Collect until end marker `[...]`
                if line.startswith('[') and line.endswith(']'):
                    if new_content:
                        jokes.append(new_content.strip())
                        new_content = ""
                    state = 1
                    i += 1
                else:
                    if line:
                        new_content += line + "\n\n"
                    i += 1

        # Update prev for debugging only (optional)
        if i >= len(lines):
            break

    # Fallback: if no jokes found, use entire body as one joke
    if not jokes:
        jokes.append(text[0].strip())

    return jokes, from_hdr


def parse_email(file_path: str):
    """
    Parse an email file into a Python `email.message.Message` object.

    Parameters
    ----------
    file_path : str
        Path to the email file (must be UTF-8 encoded text).

    Returns
    -------
    email.message.Message
        Parsed email message object.

    Raises
    ------
    SystemExit
        Exits with status code 1 and logs error if parsing fails.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return email.message_from_file(file)
    except Exception as e:
        logging.error(f"Failed to parse email: {e}")
        print(f"502 Failed to parse email: {e}")
        sys.exit(1)


def cleanup_subject(subject: str) -> str:
    """
    Clean email subject by stripping common prefixes (RE:, FW:, FWD:) and trimming whitespace.

    Handles multiple prefixes (e.g., "Re: Re: ..." → "original subject") via iteration.

    Parameters
    ----------
    subject : str
        Raw subject line.

    Returns
    -------
    str
        Cleaned subject without leading prefixes and trailing/leading whitespace.
    """
    subject = subject.strip()
    prefixes = ["re:", "fw:", "fwd:"]  # case-insensitive handling via `.lower()`

    while True:
        original_length = len(subject)
        for prefix in prefixes:
            if subject.lower().startswith(prefix):
                subject = subject[len(prefix):].strip()
                break  # only remove one prefix per iteration
        if len(subject) == original_length:
            break

    return subject


def cleanup_body(text_content: str) -> str:
    """
    Clean up raw email body text by:
    1. Removing leading `>` (reply/quote) markers per line.
    2. Collapsing multiple blank lines to single blank line.
    3. Stripping leading/trailing blank lines.

    Parameters
    ----------
    text_content : str
        Raw text content (not split into lines yet).

    Returns
    -------
    str
        Cleaned text with consistent line breaks and no quote artifacts.
    """
    lines = text_content.split('\n')

    # Pass 1: Strip leading '>' from lines (support nested quotes like ">>")
    for i in range(len(lines)):
        line = lines[i].lstrip()
        while line.startswith('>'):
            line = line[1:].lstrip()
        lines[i] = line

    # Pass 2: Collapse multiple blank lines → single blank line
    i = 0
    prev = "."
    while i < len(lines):
        if lines[i] == '' and prev == '':
            del lines[i]  # remove duplicate blank line
        else:
            prev = lines[i]
            i += 1

    # Pass 3: Remove leading/trailing blank lines
    while lines and lines[0].strip() == '':
        lines.pop(0)
    while lines and lines[-1].strip() == '':
        lines.pop()

    return '\n'.join(lines)


def extract_text_content(email_message) -> str:
    """
    Extract all `text/plain` parts from an email, joining with `-=+=-\n` separators.

    Parameters
    ----------
    email_message : email.message.Message
        Parsed email object.

    Returns
    -------
    str
        List with one string per joined part (often a list of one element).
        Content is cleaned via `cleanup_body`.
    """
    text = ""

    for part in email_message.walk():
        if part.get_content_type() == 'text/plain':
            payload = part.get_payload(decode=True)
            if payload:
                text_content = payload.decode('utf-8').strip()
                if text_content:
                    if text:
                        text += "-=+=-\n"
                    text += cleanup_body(text_content)

    return text


def extract_html_content(email_message) -> str:
    """
    Extract and convert `text/html` parts to plain text via `lynx`, then clean.

    Uses `subprocess` to invoke:
        lynx -stdin -dump -nolist -nonumbers -nounderline -width=1024 -trim_blank_lines

    Parameters
    ----------
    email_message : email.message.Message
        Parsed email object.

    Returns
    -------
    list of str
        List with one string per converted part, joined with `-=+=-\n`.
        Content is cleaned via `cleanup_body`.
    """
    text = ""

    for part in email_message.walk():
        if part.get_content_type() == 'text/html':
            payload = part.get_payload(decode=True)
            if payload:
                html_content = payload.decode('utf-8').strip()
                try:
                    process = subprocess.run(
                        ["lynx", "-stdin", "-dump", "-nolist", "-hiddenlinks=ignore",
                         "-nomargins", "-nonumbers", "-nounderline", "-width=1024",
                         "-trim_blank_lines"],
                        input=html_content,
                        text=True,
                        capture_output=True,
                        check=True
                    )
                    text_content = process.stdout.strip()
                    if text_content:
                        if text:
                            text += "-=+=-\n"
                        text += cleanup_body(text_content)
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    logging.warning(f"Failed to convert HTML with lynx: {e}")

    return text


def main():
    """
    Entry point for email joke extraction.

    Command-line arguments:
        $1 : path to email file
        $2 : output directory for extracted jokes

    Each extracted joke is written to a temporary file in `output_dir`,
    with `From:` and `Subject:` headers prepended.

    Exit Codes:
        100 : success (joke extracted)
        200 : no joke found
        500 : argument error
        501 : file not found
        502 : email parsing error
    """
    if len(sys.argv) != 3:
        print("500 Not enough arguments provided")
        sys.exit(1)

    email_file = sys.argv[1]
    output_dir = sys.argv[2]

    # Validate email file existence
    if not os.path.exists(email_file):
        logging.error(f"Email file does not exist: {email_file}")
        print(f"501 Email file does not exist: {email_file}")
        sys.exit(1)

    # Parse the email
    email_message = parse_email(email_file)

    # Extract text and HTML versions
    text_content = extract_text_content(email_message)
    html_content = extract_html_content(email_message)
    #logging.info(f"Text: {len(text_content)} HTML: {len(html_content)}")

    if text_content == html_content:
        logging.info("Text and HTML are identical.")

    # Prefer HTML if shorter (more likely to be processed clean)
    if len(text_content) >= len(html_content):
        joke_content = [text_content]
        logging.info("Using Text version")
    else:
        joke_content = [html_content]
        logging.info("Using HTML version")

    if joke_content and joke_content[0]:
        from_header = email_message.get('From', '').strip()
        subject_header = cleanup_subject(email_message.get('Subject', '').strip())

        # Apply custom parsers for known sources
        if from_header == "You Make Me Laugh <Crosswalk@crosswalkmail.com>":
            joke_content, subject_header = parse_You_Make_Me_Laugh(joke_content, subject_header)
        elif "aardvark@illinois.edu" in from_header:
            subject_header = '' # subject is never a good title for any joke in the email :(
            joke_content, from_header = parse_Sanderson(joke_content)

        # Write each joke to a temp file in output dir
        for joke in joke_content:
            with tempfile.NamedTemporaryFile(
                mode='w',
                prefix='joke_',
                suffix='.txt',
                dir=output_dir,
                delete=False
            ) as tmp_file:
                tmp_file.write(f"Title: {subject_header}\n")
                tmp_file.write(f"From: {from_header}\n")
                tmp_file.write("\n")  # separator
                tmp_file.write(joke)

            logging.info(f"Successfully extracted joke to {tmp_file.name}")
        print("100 Successfully extracted joke")
    else:
        logging.info("No joke content found")
        print("200 No joke found")


if __name__ == "__main__":
    main()
