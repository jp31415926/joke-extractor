# parser-hints.md for Mikey's Funnies

- Text format is the only format available.

- There will only be one joke per email.

- Use `"funnies-owner@lists.MikeysFunnies.com" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` cannot be used as the title. There is no valid title in these emails. use title = "".

- The start marker is a line that starts with "Today's Funny". The start delimiter should not be included in the joke text.

- The rest of the text is the joke text, until you see the end marker.

- The end marker is a line that starts with "Today's Thot". Do not include that line with the joke.
