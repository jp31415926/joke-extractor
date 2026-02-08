"""Parser for Best of Humor emails."""

# SEE EXAMPLE EMAIL AT BOTTOM OF FILE

from . import register_parser

def _is_best_of_humor(from_header: str) -> bool:
    return "bestofhumor.com" in from_header or "shawn@bestofhumor.com" in from_header

@register_parser(_is_best_of_humor)
def parse(text: list, subject: str) -> tuple:
    """
    Parse 'Best of Humor' email format.

    Jokes are embedded between visual separator lines like:
        +--------------...------------+
        or
        ++-...--++

    Each joke is the text *between* such lines (or between a line and email start/end).

    The email footer (signature, unsubscribe, newsletter sign-ups, promotions)
    is excluded. Only substantial jokes (≥2 lines, non-promotional) are returned.

    Parameters
    ----------
    text : list of str
        List containing a single string of the email's text/plain content.

    Returns
    -------
    tuple
        - list[str]: List of extracted joke bodies (cleaned).
        - str: Always '' (subject is never used as a title).
    """
    # Extract full text
    raw = text[0]

    lines = raw.split('\n')

    # Identify border lines: start with '+' and contain '-' or '=' and end with '+'
    # Examples: "+--------------...", "++-...--++"
    border_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if ((stripped.startswith('+') and stripped.endswith('+')) or 
            (stripped.startswith('~') and stripped.endswith('~')) or
            (stripped.startswith('_') and stripped.endswith('_'))):
            border_indices.append(i)

    # If no borders found, fall back to entire body
    if not border_indices:
        return [raw.strip()], ''

    jokes = []

    # Collect sections between borders (including start-to-first and last-to-end)
    sections = []
    if border_indices:
        # Section 0: before first border
        sections.append((0, border_indices[0]))
        # Sections between borders
        for i in range(len(border_indices) - 1):
            start = border_indices[i] + 1
            end = border_indices[i + 1]
            sections.append((start, end))
        # Section N: after last border until end
        sections.append((border_indices[-1] + 1, len(lines)))

    for start, end in sections:
        candidate_lines = lines[start:end]
        # Clean candidate: strip blank lines
        candidate = '\n'.join(candidate_lines).strip()
        if not candidate:
            continue

        # Skip obvious non-joke content:
        # - pure promotion/subscribe lines (start with http, "<a", "Join", etc.)
        # - lines with only links or URLs
        # - lines that are pure footer/signature-like
        lines_to_keep = []
        for line in candidate.split('\n'):
            line_stripped = line.strip()
            # Skip pure URLs or promotional lines
            if ('http' in line_stripped or
                '<a' in line_stripped.lower() or
                'mailto:' in line_stripped or
                line_stripped.lower().startswith('subscribe') or
                line_stripped.lower().startswith('join') or
                line_stripped.lower().startswith('unsub') or
                line_stripped.startswith('___') or
                'Bestofhumor.com' in line_stripped or
                'email4fun' in line_stripped or
                line_stripped.lower().startswith('visit') and 'http' in line_stripped):
                continue
            lines_to_keep.append(line)

        cleaned_candidate = '\n'.join(lines_to_keep).strip()
        if not cleaned_candidate:
            continue

        # Require at least 2 non-empty lines to avoid noise (e.g., one-line ads)
        non_empty_lines = [l for l in cleaned_candidate.split('\n') if l.strip()]
        if len(non_empty_lines) < 2:
            continue

        # Skip if mostly promo (e.g., >50% lines contain 'free', 'win', 'click', etc.)
        promo_keywords = ['free', 'win', 'click', 'enter now', 'subscribe', 'join', 'visit']
        promo_count = sum(
            any(kw in line.lower() for kw in promo_keywords)
            for line in non_empty_lines
        )
        if promo_count / len(non_empty_lines) > 0.5:
            continue

        jokes.append(cleaned_candidate)

    # Fallback: if no jokes found, use entire body
    if not jokes:
        jokes.append(raw.strip())

    return jokes, ''

"""
Subject: Best of Humor July 13th
From: "Bestofhumor.com" <shawn@bestofhumor.com>

Welcome to Best of Humor ---> http://www.bestofhumor.com
We are part of the email4fun.com network ---> http://www.email4fun.com
For FREE Fun E-mail, Visit http://sjMail.com

-------------- LIST INFORMATION -----------------
You are subscribed as: gcfl-submit@gcfl.net
To unsubscribe send an email to
<A href="mailto:bestofhumor-leave@list2.sjmail.com">unsubscribe</A>
Or go to:  http://www.bestofhumor.com/leave.html
Join Best of Humor:  http://www.bestofhumor.com/subscribe.html
-------------- LIST INFORMATION -----------------

NOTE:  We had some computer problems on our end the past couple days.  We 
are finalizing our move to a new lyris server.  Don't worry all of you are 
coming with me to hopefully a faster server

+---------------------------------------------------------------+
Win a Complete home theater!
It's a super System! A 53" Big Screen TV!

Surround Sound System, CD/DVD Player.
Two leather recliners.
What do you have to lose? Enter now!
This offer expires 08/04/00.
http://www.afreeplace.com/boh/super.htm
<a href="http://www.1freeplace.com/boh/super.htm">AOL link</a>
+---------------------------------------------------------------+

A painter, whitewashing the inner walls of a country outhouse,
had the misfortune to fall through the opening and land in the
muck at the bottom. He shouted, "Fire! Fire! Fire!" at the top
of his lungs.

The local fire department responded with alacrity, sirens
roaring as they approached the privy.

"Where's the fire?" called the chief.

"No fire," replied the painter as they pulled him out of the hole.

"But if I had yelled, 'Shit! Shit! Shit!' who would have rescued me?"

+---------------------------------------------------------------+
FREE E-MAIL ENTERTAINMENT
List World is the place to go to get all the free
newsletters you want! Join a free newsletter now!
http://www.listworld.net/index23b.cfm?refid=24
<A href="http://www.listworld.net/index23b.cfm?refid=24">FREE NEWSLETTERS</A>
+---------------------------------------------------------------+

Amanpreet was having marital problems. So he went to his

The shrink says "when you get home, throw down your
briefcase, run to her, embrace her, take off her clothes, and
yours, and make made passionate love to her."
In two weeks Preet was back in the shrink's office. The shrink
asked "How did it go?"

Preet said, "She didn't have anything to say, but her bridge
club got a kick out of it."

~~~~~~~~~~~~~~~~
Shawn Thayer
Best of Humor
http://www.bestofhumor.com
shawn@bestofhumor.com

_______  Bestofhumor.com Daily Humor  _______
You are subscribed as: gcfl-submit@gcfl.net
To unsubscribe send an email to 
mailto:leave-bestofhumor-284604L@list2.sjMail.com
Or go to:  http://www.bestofhumor.com/leave.html

We are part of the email4fun.com network ---> http://www.email4fun.com
"""