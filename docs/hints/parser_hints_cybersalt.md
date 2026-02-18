# parser-hints.md for Cybersalt Digest

- HTML format preferred, unless empty.

- There will only be one joke per email.

- Use `"posts@cybersaltlists.org" in email.from_header.lower()` to match the email to this parser.

- For this parser, `email.subject_header` will never be used for the return title. It doesn't describe the joke.

- The start delimiter is the line that starts with "Here is today's CleanLaugh". The start delimiter should not be included in the joke text.

- If the email does not have the "Here is today's CleanLaugh" line, that email doesn't have a joke at all; return [].

- The `joke.title` is in the same line as the start marker. The title come directly after "Here is today's CleanLaugh. - ". For example, for 'Here is today's CleanLaugh - "Ten Commandments"' the title is "Ten Commandments" (without the quotes). Don't include the quotes in the title.

- The rest of the text is the joke text, until you see the end delimiter.

- The end delimiter is the line "You can rate this joke at:". Do not include that line with the joke.
