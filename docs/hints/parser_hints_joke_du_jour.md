# parser-hints.md for Joke du Jour

- Text format is the only format available.

- There could be multiple jokes per email.

- Use `"ladyhawke@jokedujour.com" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` cannot be used as the title.

1. The start marker for the first joke is a line that equals `~*~*~*~*~*~*`. The start marker should not be included in the joke text. The start marker for additional jokes (if present) will be specified below.

2. The first non-blank line after the start marker may be the title in quotes, or a line that starts with `<>*<>` signifying the end of the valid content. If it is quoted text, there may be other text before or after the quoted text. Extract only the text in quotes and use that as a title. If end of valid content, ignore all remaining lines.

3. If we are not done, the rest of the text is the joke text, until you see the end marker.

4. The end marker is a line that starts with "http". Do not include that line with the joke. This line starts an ad, but it will be repeated to mark the end of the ad. Skip over the ad.

5. After the end of the ad, assume you have seen a start marker and go to step 2.
