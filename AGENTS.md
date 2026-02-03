# AGENTS.md - Joke Extractor Project

## Build, Lint, and Test Commands

### Build Commands
- `python3 joke-extract.py <path_to_eml_file>` - Run the main application
- `chmod +x *.py` - Make scripts executable as needed

### Lint Commands
- `python -m flake8 .` - Check code style and format
- `python -m pyflakes .` - Check for syntax errors and undefined names
- `python -m pylint .` - Run full code analysis

### Test Commands
- `python3 -m pytest tests/` - Run all unit and integration tests
- `python3 tests/integration_test.py` - Run integration test specifically
- `python3 extractors/default.py tests/valid.eml ./jokes/` - Test individual extractor
- `python3 joke-extract.py tests/valid.eml` - Test primary script with valid file
- `python3 -m pytest tests/ -v` - Run tests with verbose output
- `python3 -m pytest tests/ -k "test_"` - Run tests matching pattern "test_" 

For running a single test:
- `python3 -m pytest tests/test_default_extractor.py::test_valid_plain_text -v`

## Code Style Guidelines

### General
- Use Python 3.11+
- Strict UTF-8 encoding for all files
- All scripts must have shebangs (`#!/usr/bin/env python3`)
- Use the `logging` module for all output instead of `print()`
- All code must be executable and follow the specification exactly

### Imports
- Use standard library modules only: `sys`, `os`, `email`, `tempfile`, `logging`, `subprocess`, `argparse`
- Import modules at the top of each file in standard order:
  1. Standard library imports
  2. Third-party imports (none in this project)
  3. Local application imports (none in this project)
- Import individual modules rather than using wildcard imports: `from email import message_from_file` instead of `from email import *`

### Formatting
- Indentation: 4 spaces (no tabs)
- Line length: Maximum 88 characters (PEP8 + black)
- No trailing whitespace
- Use snake_case for variables and functions
- Use PascalCase for classes
- Single blank lines to separate logical sections of code
- Double blank lines to separate top-level function or class definitions

### Naming Conventions
- Variables: `snake_case` (e.g., `email_message`, `output_dir`)
- Constants: `UPPER_CASE` (e.g., `MAX_RETRIES`)
- Functions: `snake_case` (e.g., `parse_email`, `extract_joke`)
- Classes: `PascalCase` (e.g., `EmailExtractor`)
- Private methods: `_snake_case` (e.g., `_validate_headers`)

### Error Handling
- Exit with `sys.exit(1)` on validation failures (file existence, missing headers, invalid attachments)
- Handle exceptions gracefully in email parsing and file operations
- Return appropriate exit codes from extractors:
  - `100-199`: Success (stop processing)
  - `200-299`: No joke found (continue)
  - `500-599`: Error (continue but warn)
- Use logging for status information:
  - `logging.debug()` for return codes `100-199`
  - `logging.warning()` for return codes `500-599`
  - Error messages should be descriptive but concise

### Return Codes
- Extractors must return one of these codes (exit code 0 for all cases):
  - `100`: Success - joke extracted
  - `200`: No joke found
  - `500`: Failed to parse email
  - `501`: Other error during processing

### File Handling
- All email files must be processed with UTF-8 encoding
- Use `tempfile.NamedTemporaryFile` with `prefix="joke_"` and `suffix=".txt"` for output files
- Extractors must write to the directory specified in the second CLI argument
- Don't modify the original EML files
- All output files must be created atomically

### Testing
- All test fixtures are real RFC-style EML files in the `tests/` directory
- Extractor scripts should work as subprocesses from the main script
- Extractors must validate all input and handle edge cases properly
- Integration tests should exercise the full pipeline end-to-end