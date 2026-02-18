# parser-hints.md for Best of Humor

- [x] Text format is preferred
- [ ] HTML format is preferred

- What to do if preferred format is empty?
- [ ] Use other format
- [x] return empty list (e.g. `[]`)

- How many jokes are expected?
- [ ] Only one
- [ ] Specific number:
- [x] Multiple, but no specific number

- Expression to match this parser: `"shawn@bestofhumor.com" in email.from_header.lower()`

- [ ] Yes use `email.subject_header` for the title
- [x] No don't use `email.subject_header` for the title

- The the start of joke marker (SOJ) is a line that 
  - starts with `+--` and ends with `--+` or
  - starts with `++-` and ends with `-++` or 
  - ends with `<<<<` or
  - starts with `------------------------------` (30x'-')

- [x] The rest of the text is the joke text, until you see the end of joke marker (EOJ).

- The EOJ also marks the start of the next joke.

- The end of file marker (EOF) is a line that
  - starts with `~~~~~` or 
  - starts with `_____` or
  - equals `---`
- When the EOF occurs, ignore the remainder of the email.
- If you reach the last line, discard what you have collected.

- [ ] Yes include the markers in the joke
- [x] No don't include the markers in the joke

- Are the paragraphs line wrapped, or one long line?
- [x] Yes - concatenate multiple non-blank lines together into one long line; preserve blank lines between paragraphs.
- [ ] No - insert a blank line between every non-blank line (each like is always a full paragraph).

- [x] Yes reduce multiple consecutive blank lines to one blank line
- [ ] No don't reduce multiple consecutive blank lines to one blank line

## Additional Info
Follow these rules in this order:
- If the first line of the joke contains `http`, discard that line and continue processing the rest of the joke.
- If a joke contains the following strings (case insensitive) on any line in the joke, the entire joke should be discarded:
  - `http`
  - `mailto`
  - `copyright`
- If any line in a joke contains `bestofhumor.com` or `free t-shirt`, discard that line and continue processing the rest of the joke.
