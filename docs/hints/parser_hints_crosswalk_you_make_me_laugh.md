# parser-hints.md for Crosswalk - You Make Me Laugh

- Text format is preferred unless it is empty.

- There will only be one joke per email.

- Use `"You_Make_Me_Laugh@lists.crosswalk.com" in email.from_header.lower()` to match the email to this parser.

- `email.subject_header` can be used as the title. Remove the prefix "Crosswalk - You Make Me Laugh: " and the suffix comma and date. Remove the quotes from the title. Example: `Crosswalk - You Make Me Laugh: "First Apartment", July 30, 2004` -> `First Apartment`

- The start marker is the same title pulled from the Subject header, with asterisks on both sides. Example: `*First Apartment*`. The start marker should not be included in the joke text.

- The rest of the text is the joke text, until you see the end marker.

- The end marker is line that contains "cybersalt.org/cleanlaugh". Do not include that line with the joke.

- If the last line of the identified joke has asterisks on both sides, remove that line. Example: `*Thanks to Pastor Tim for this joke!*`
