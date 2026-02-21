# parser-hints.md for Best of Humor

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [ ] Use other format
- [x] return empty list (e.g. `[]`)

- How many jokes are expected?
- [x] Only one
- [ ] Specific number:
- [ ] Multiple, but no specific number

- if the first non-blank line contains and alphanum characters, assume it is the title. Remove all non-alphanum characters from the beginning and end of the title.
- any line containing 'http' or 'mailto' should be deleted.
- any joke that contains 'copyright' should be delete.

- Expression to match this parser: `"bill@billrayborn.com" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title

- The entire message is the joke.

- [ ] Line wrapped - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [x] One lone line - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line

