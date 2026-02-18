# parser-hints.md for Gag-O-Matic Joke Server

- Text format is the only format available.

- There will only be one joke per email.

- Use `"jokes@gag-o-matic.lowcomdom.com" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` can be used as the title. Remove any trailing periods in the title.

- There is no start marker. The first line starts with the joke.

- The rest of the text is the joke text, until you see the end marker.

- The end marker is another line that starts with "Gag-O-Matic Joke Server". Do not include that line with the joke.
