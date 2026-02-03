import pytest

def test_integration():
    result = pytest.main([-v, tests/])
    assert jokes/valid_plain.txt in open(jokes/valid_plain.txt).read()
    assert result.returncode == 0
