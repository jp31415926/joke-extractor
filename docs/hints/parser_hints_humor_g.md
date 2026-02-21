# parser-hints.md for Humor_G

- HTML format is the preferred format unless it is blank.

- There will only be one joke per email.

- Use `"judib51@comcast.net" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` cannot be used as the title. However, if `email.subject_header.lower()` contains "toon" or "good ole maxine" or "attachment" in the subject, discard the email and return []

- There is no start marker. The first line starts with the joke.

- The rest of the text is the joke text, until you see the end marker.

- The end marker is a line that starts with "~~~~~~~~~~" (10x'~'). Do not include that line with the joke.

- If `[cid:` or `http` occurs anywhere in the joke, the joke is to be discarded and return [].
