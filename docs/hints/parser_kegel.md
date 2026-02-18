# parser-hints.md for **FILL IN PARSER NAME**

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [x] Use other format
- [ ] return empty list (e.g. `[]`)

- How many jokes are expected?
- [x] Only one
- [ ] Specific number: ___
- [ ] Multiple, but no specific number

- Expression to match this parser: `"tellswor@kcbx.net" in email.from_header.lower()`

- [x] Yes use `email.subject_header` for the title
- [ ] No don't use `email.subject_header` for the title
  - Additional notes:

- The start marker is: a line that starts with ***FILL IN THE START MARKER HERE***

- [ ] Yes include the start marker in the joke
- [x] No don't include the start marker in the joke

- [x] The rest of the text is the joke text, until you see the end marker.

- The end marker is: a line that starts with ***FILL IN THE END MARKER HERE***

- [ ] Yes include the end marker in the joke
- [x] No don't include the end marker in the joke

- Are the paragraphs line wrapped, or one long line?
- [x] Yes - concatinate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [ ] No - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line
