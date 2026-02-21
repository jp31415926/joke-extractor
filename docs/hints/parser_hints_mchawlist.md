# parser-hints.md for McHawList

- Use `title()` to correct title capitalization

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [x] Use other format
- [ ] return empty list (e.g. `[]`)

- How many jokes are expected?
- [ ] Only one
- [ ] Specific number: ___
- [x] Multiple, but no specific number

- Expression to match this parser: `"ksullivan@worldnet.att.net" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title
  - Additional notes: Title is the first line of each joke

- The start marker is: the first joke starts on line 1. If line 1 starts with "From: Keith Sullivan", skip it and start at the first non-blank line. The start marker for additional jokes is the same line as the end marker.

- [ ] Yes include the start marker in the joke
- [x] No don't include the start marker in the joke

- [x] The rest of the text is the joke text, until you see the end marker

- The end marker is: a line that starts with "=-=-=-=-=-" if another joke follows. If the line starts with "----------" there will be no more jokes. Ignore the remaining lines.

- [ ] Yes include the end marker in the joke
- [x] No don't include the end marker in the joke

- Are the paragraphs line wrapped?
- [x] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [ ] No - insert a blank line between every non-blank line (each line is always a full paragraph).

Remove excess blank lines?
- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line
- [x] Yes remove all blank lines before and after the joke
- [ ] No don't remove all blank lines before and after the joke

## Additional Info
- If a joke contains `http`, `mailto` or `copyright` (case insensitive) on any line in the joke, return []:
