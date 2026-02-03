import subprocess
import sys

def test_integration():
    result = subprocess.run([sys.executable, joke-extract.py, tests/valid_plain.eml], capture_output=True, text=True)
    assert jokes/valid_plain.txt in result.stdout
    assert result.returncode == 0
