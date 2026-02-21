#!/usr/bin/env python3
"""Integration tests: run joke-extract.py end-to-end against real .eml files.

Each test sends a real newsletter email through the full extraction pipeline
(subprocess → joke-extract.py) and asserts:
  1. Exit code 100 (jokes extracted successfully).
  2. The expected number of joke files was written to the success dir.
  3. At least one key phrase appears somewhere in the extracted content.
"""

import glob
import os
import subprocess
import sys
import tempfile

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(_HERE, '..', 'joke-extract.py')
_EMAILS = os.path.join(_HERE, 'emails')


def _run(eml_filename):
  """Run joke-extract.py on a test email.

  Returns
  -------
  tuple[int, list[str]]
      (exit_code, list of joke file contents)
  """
  eml_path = os.path.join(_EMAILS, eml_filename)
  with (
    tempfile.TemporaryDirectory() as success_dir,
    tempfile.TemporaryDirectory() as failure_dir,
  ):
    result = subprocess.run(
      [sys.executable, _SCRIPT, eml_path, success_dir, failure_dir],
      capture_output=True,
      text=True,
    )
    code = int(result.stdout.strip().split()[0])
    jokes = []
    for path in sorted(glob.glob(os.path.join(success_dir, 'joke_*.txt'))):
      with open(path) as f:
        jokes.append(f.read())
    return code, jokes


def _contains(jokes, phrase):
  """Return True if phrase appears (case-insensitively) in any joke text."""
  phrase_lower = phrase.lower()
  return any(phrase_lower in joke.lower() for joke in jokes)


# ---------------------------------------------------------------------------
# Parser: Best of Humor  (shawn@bestofhumor.com)
# ---------------------------------------------------------------------------

def test_best_of_humor():
  code, jokes = _run('Best of Humor July 13th.eml')
  assert code == 100
  assert len(jokes) == 2
  assert _contains(jokes, 'painter')


# ---------------------------------------------------------------------------
# Parser: Christian Voices  (GrampsTN@comcast.net)
# ---------------------------------------------------------------------------

def test_christian_voices():
  code, jokes = _run('Christian Voices August 29, 2007.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'Every takeoff is optional')


# ---------------------------------------------------------------------------
# Parser: Crosswalk - You Make Me Laugh  (you_make_me_laugh@lists.crosswalk.com)
# ---------------------------------------------------------------------------

def test_crosswalk_you_make_me_laugh():
  code, jokes = _run("Crosswalk - You Make Me Laugh '14 Letters', July 5, 2004.eml")
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'Robert and Peter')


# ---------------------------------------------------------------------------
# Parser: Cybersalt  (posts@cybersaltlists.org)
# ---------------------------------------------------------------------------

def test_cybersalt():
  code, jokes = _run('[Cybersalt Digest] Issue #3444.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'college football player')


# ---------------------------------------------------------------------------
# Parser: Ellsworth  (tellswor@kcbx.net)
# ---------------------------------------------------------------------------

def test_ellsworth():
  code, jokes = _run('GCF Colorful Meal.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'colorful meal')


# ---------------------------------------------------------------------------
# Parser: Gag-O-Matic  (jokes@gag-o-matic.lowcomdom.com)
# ---------------------------------------------------------------------------

def test_gag_o_matic():
  code, jokes = _run('Earth.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'post card')


# ---------------------------------------------------------------------------
# Parser: Humor_G  (judib51@comcast.net)
# ---------------------------------------------------------------------------

def test_humor_g():
  code, jokes = _run('[Humor_G] Humor_G.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'Obama')


# ---------------------------------------------------------------------------
# Parser: Joke du Jour  (ladyhawke@jokedujour.com)
# ---------------------------------------------------------------------------

def test_joke_du_jour():
  code, jokes = _run('JdJ Oct 10, 01 Favorite Vacations Spots of.....eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'Painted Desert')


# ---------------------------------------------------------------------------
# Parser: McHawList  (ksullivan@worldnet.att.net)
# ---------------------------------------------------------------------------

def test_mchawlist():
  code, jokes = _run('[McHawList] The Beatles.eml')
  assert code == 100
  assert len(jokes) == 7
  assert _contains(jokes, 'Leonardo da Vinci')


# ---------------------------------------------------------------------------
# Parser: Merry Hearts  (tanger@lvbaptist.org)
# xfail: parser does not find the header "A   M E R R Y   H E A R T" because
# it searches for the contiguous substring "MERRY" which the spaced format
# does not contain.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
  strict=False,
  reason="parser_merry_hearts fails to locate 'A   M E R R Y   H E A R T' header",
)
def test_merry_hearts():
  code, jokes = _run("[merry-hearts] Steve Wonder's Golf Game.eml")
  assert code == 100
  assert len(jokes) >= 1
  assert _contains(jokes, 'Steve Wonder')


# ---------------------------------------------------------------------------
# Parser: Mikey's Funnies  (funnies-owner@lists.mikeysfunnies.com)
# ---------------------------------------------------------------------------

def test_mikeys_funnies():
  code, jokes = _run('01.10 A Shot Funny.eml')
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'naval barracks')


# ---------------------------------------------------------------------------
# Parser: Sanderson  (aardvark@illinois.edu)
# ---------------------------------------------------------------------------

def test_sanderson():
  code, jokes = _run('Sunday Fun Stuff DECISION MADE.eml')
  assert code == 100
  assert len(jokes) == 2
  assert _contains(jokes, 'travel agent')


# ---------------------------------------------------------------------------
# Parser: You Make Me Laugh  (crosswalk@crosswalkmail.com)
# ---------------------------------------------------------------------------

def test_you_make_me_laugh():
  code, jokes = _run(
    'Acts 2 38 - August 26, 2010 - You Make Me Laugh'
    ' (Crosswalk@crosswalkmail.com) - 2026-02-04 2237.eml'
  )
  assert code == 100
  assert len(jokes) == 1
  assert _contains(jokes, 'burglar')
