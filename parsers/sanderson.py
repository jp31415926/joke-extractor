"""Parser for Steve Sanderson's 'Sunday Fun Stuff' emails."""

from . import register_parser

def _is_sanderson(from_header: str) -> bool:
    return "aardvark@illinois.edu" in from_header

@register_parser(_is_sanderson)
def parse(text: list, subject: str):
    """
    Parse Steve Sanderson's "Sunday Fun Stuff" email format.

    This parser identifies jokes delimited by:
    - Start marker: `*` repeated =10 times (`**********`)
    - Title: a line ending with `:`
    - Joke body: lines up until the next `[...]:`-style closing tag (e.g., `[end]`)
    - Ends at a line containing exactly `Steve Sanderson`

    Parameters
    ----------
    text : list of str
        List containing a single string of the email's text/plain content.
    subject : str
        Subject line � unused because Sanderson email Subjects don't describe the jokes themselves

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
                    # No title � jump to content (non-standard)
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

    # Fallback: if no jokes found, use entire body as one joke
    if not jokes:
        jokes.append(text[0].strip())

    return jokes, from_hdr
