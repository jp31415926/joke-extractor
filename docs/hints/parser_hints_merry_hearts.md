# parser-hints.md for Merry Hearts

- [ ] Text format is preferred
- [x] HTML format is preferred

- What to do if preferred format is empty?
- [x] Use other format
- [ ] return empty list (e.g. `[]`)

- How many jokes are expected?
- [x] Only one
- [ ] Specific number: ___
- [ ] Multiple, but no specific number

- Expression to match this parser: `"tanger@lvbaptist.org" in email.from_header.lower()`

- [x] Yes use `email.subject_header` for the title
- [ ] No don't use `email.subject_header` for the title
  - Additional notes: Remove the prefix `"[merry-hearts] "` from the subject header.

- The start marker is: a line that starts with "----------" or "*:-.,_,.-:*'``'"

- [ ] Yes include the start marker in the joke
- [x] No don't include the start marker in the joke

- [x] The rest of the text is the joke text, until you see the end marker.

- The end marker is: a line that starts with "=========="

- [ ] Yes include the end marker in the joke
- [x] No don't include the end marker in the joke

- Are the paragraphs line wrapped, or one long line?
- [ ] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [x] No - insert a blank line between every non-blank line (each line is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line
