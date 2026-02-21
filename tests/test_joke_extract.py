#!/usr/bin/env python3
"""Tests for joke-extract.py using synthetic .eml fixtures in tests/.

These cover edge cases at the pipeline level: missing content, no parser
match, bad arguments, missing files, etc.
"""

import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(_HERE, '..', 'joke-extract.py')


def _run(fixture_name):
  """Run joke-extract.py on a fixture file; return (exit_code, stdout_code)."""
  eml_path = os.path.join(_HERE, fixture_name)
  with (
    tempfile.TemporaryDirectory() as success_dir,
    tempfile.TemporaryDirectory() as failure_dir,
  ):
    result = subprocess.run(
      [sys.executable, _SCRIPT, eml_path, success_dir, failure_dir],
      capture_output=True,
      text=True,
    )
    stdout_code = int(result.stdout.strip().split()[0])
    return result.returncode, stdout_code


def test_plain_text_no_parser_match():
  """Email with plain text but no matching parser → stdout 201."""
  _, code = _run('plain_text.eml')
  assert code == 201


def test_html_only_no_parser_match():
  """Email with HTML only but no matching parser → stdout 201."""
  _, code = _run('html_only.eml')
  assert code == 201


def test_empty_text_no_content():
  """Email whose text parts are empty → stdout 200."""
  _, code = _run('empty_text.eml')
  assert code == 200


def test_no_text_no_content():
  """Email with no text/html parts at all → stdout 200."""
  _, code = _run('no_text.eml')
  assert code == 200


def test_missing_from_no_parser_match():
  """Email with blank From header → stdout 201 (no parser matched)."""
  _, code = _run('missing_from.eml')
  assert code == 201


def test_invalid_attachment_no_content():
  """Email with only an unrecognised attachment → stdout 200."""
  _, code = _run('invalid_attachment.eml')
  assert code == 200


def test_missing_file_exits_nonzero():
  """Non-existent email file → process exit 1, stdout starts with 501."""
  with (
    tempfile.TemporaryDirectory() as success_dir,
    tempfile.TemporaryDirectory() as failure_dir,
  ):
    result = subprocess.run(
      [sys.executable, _SCRIPT, 'nonexistent.eml', success_dir, failure_dir],
      capture_output=True,
      text=True,
    )
  assert result.returncode == 1
  assert result.stdout.strip().startswith('501')


def test_too_few_args():
  """No arguments at all → process exit 1, stdout starts with 500."""
  result = subprocess.run(
    [sys.executable, _SCRIPT],
    capture_output=True,
    text=True,
  )
  assert result.returncode == 1
  assert result.stdout.strip().startswith('500')
