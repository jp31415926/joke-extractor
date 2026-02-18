# parser-hints.md for Thomas S. Ellsworth

- Text format is the only formar available.

- There will only be one joke per email.

- Use `"tellswor@kcbx.net" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` can be used as the title. Remove the prefix "GCF: ".

- The start marker is a line that starts with "----------" (10x'-'). The start delimiter should not be included in the joke text.

- The first line after the start marker should be a repeat of the subject. If so, don't include it in the joke.

- The rest of the text is the joke text, until you see the end marker.

- The end marker is another line that starts with "----------" (10x'-'). Do not include that line with the joke.
