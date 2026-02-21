# parser-hints.md for WITandWISDOM

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [ ] Use other format
- [x] return empty list (e.g. `[]`)

- How many jokes are expected?
- [ ] Only one
- [x] Specific number: 2
- [ ] Multiple, but no specific number

- Expression to match this parser: `"richardw@olypen.com" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title

- The first start marker is `~~~~~~~ THIS & THAT:` and the second start marker is `~~~~~~~ KEEP SMILING:`. There will always be exactly two jokes.

- [ ] Yes include the start marker in the joke
- [x] No don't include the start marker in the joke

- [x] The rest of the text is the joke text, until you see the end marker.

- The end marker is a line that starts with `~~~~~~~`. The end marker and the start marker of the second joke will most likely be the same line. Since there will always be only two jokes, when you see the second end marker, ignore the remainder of the email.

- [ ] Yes include the end marker in the joke
- [x] No don't include the end marker in the joke

- Are the paragraphs line wrapped, or one long line?
- [x] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [ ] No - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line
