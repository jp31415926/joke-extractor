Parsing hints for the Christian Voices parser follow.

- For this parser, the Subject: will never be used for the return subject. It doesn't describe the joke.

- All the text before the line that starts with "HUMOR" should be ignored. The HUMOR line marks the beginning of the joke. The HUMOR like should not be included in the joke text.

- If the email does not have the HUMOR line, that email doesn't have a joke at all; return an empty text string.

- The next non-blank line after the HUMOR line is the subject, if it is less than 35 characters. If it is longer, there was no subject provided, so return subject = "".

- The rest of the text is the joke text, until you see the end delimiter.

- The end delimiter starts with the 4-character string "<>< ". Do not include that line with the joke.

