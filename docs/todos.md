# todo.md

This checklist is designed to be updated as the build agent completes each step of the Joke Extractor project, following the `orchestrator-blueprint.md` and `spec.md` specifications.

## Phase 1: Environment & Test Data

### Step 1: Project Scaffolding
- [ ] Create project directories: `extractors/`, `tests/`, and `jokes/`
- [ ] Initialize `joke-extract.py` with shebang and executable permissions
- [ ] Initialize `extractors/default.py` with shebang and executable permissions
- [ ] Verify `ls -R` output shows correct directory structure
- [ ] Verify `chmod +x` status on scripts
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 2: RFC-Compliant Test Fixtures
- [ ] Create `tests/valid_plain.eml` with Subject, From, and non-empty `text/plain`
- [ ] Create `tests/valid_html.eml` with Subject, From, and non-empty `text/html`
- [ ] Create `tests/empty_body.eml` with `text/plain` but empty content
- [ ] Create `tests/invalid_attachment.eml` with `application/pdf` part
- [ ] Create `tests/missing_from.eml` with empty `From:` header
- [ ] Verify each `.eml` file loads without crashing using `email.message_from_file()`
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

## Phase 2: Extractor Development (`extractors/default.py`)

### Step 3: Argument & Email Parsing
- [ ] Implement CLI argument handling for 2 arguments
- [ ] Implement `email.message_from_file()` parsing with UTF-8 enforcement
- [ ] Verify `extractors/default.py tests/valid_plain.eml ./jokes/` exits with code 0
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 4: MIME Priority Logic
- [ ] Implement part scanning logic
- [ ] Prioritize `text/plain` exactly before falling back to `text/html`
- [ ] Ignore non-text parts
- [ ] Verify `valid_plain.eml` prints `100 Success`
- [ ] Verify `empty_body.eml` prints `200 No joke found`
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 5: Atomic File Writing
- [ ] Use `tempfile.NamedTemporaryFile` with `prefix="joke_"` and `suffix=".txt"`
- [ ] Write content to `output_dir` correctly
- [ ] Verify file appears in `jokes/` after running against `valid_plain.eml`
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

## Phase 3: Primary Script Development (`joke-extract.py`)

### Step 6: Input Validation
- [ ] Implement `sys.exit(1)` for file readability issues
- [ ] Implement `sys.exit(1)` for missing Subject header
- [ ] Implement `sys.exit(1)` for empty From header
- [ ] Implement `sys.exit(1)` for non-text attachments
- [ ] Verify `joke-extract.py tests/invalid_attachment.eml` exits with code 1
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 7: Extractor Orchestration
- [ ] Implement discovery of `extractors/` directory (alphabetical order)
- [ ] Implement subprocess execution of each extractor
- [ ] Implement stdout capture of first line (format: `### <message>`)
- [ ] Verify logging shows captured 100 Success string when running with DEBUG logging
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 8: Return Code & Early Exit
- [ ] Implement logic to stop processing on return codes `100-199`
- [ ] Implement logic to continue processing on return codes `200-299`
- [ ] Implement logic to log warning on return codes `500-599`
- [ ] Verify `joke-extract.py tests/valid_plain.eml` exits with code 0
- [ ] Verify `joke-extract.py tests/empty_body.eml` exits with code 1
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

## Phase 4: Final Integration

### Step 9: End-to-End Testing
- [ ] Create `tests/integration_test.py` that invokes full pipeline
- [ ] Verify integration test asserts existence of joke file in `jokes/`
- [ ] Run `pytest tests/` or `python3 tests/integration_test.py`
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)

### Step 10: Cleanup & Audit
- [ ] Remove all `print()` statements from code
- [ ] Ensure all logs use the `logging` module
- [ ] Confirm UTF-8 compliance throughout project
- [ ] Verify `grep -r "print(" .` returns no results
- [ ] Verify all scripts have proper shebangs (`#!/usr/bin/env python3`)
- [ ] Verify all required imports are standard library modules only
- [ ] Run linting tools: `flake8`, `pyflakes`, `pylint` to ensure compliance
- [ ] Performed checks listed below in the **Code Style Compliance** section (where applicible)
- [ ] Performed checks listed below in the **Error Handling & Return Codes** section (where applicible)
- [ ] Performed checks listed below in the **File Handling** section (where applicible)


## Additional Checks
These should be checked for every step, As applicible.

### Code Style Compliance
- [ ] All scripts use Python 3.11+
- [ ] All files use strict UTF-8 encoding
- [ ] All scripts have shebangs
- [ ] All output uses `logging` module instead of `print()`
- [ ] Indentation uses 4 spaces
- [ ] Line length does not exceed 88 characters
- [ ] No trailing whitespace
- [ ] Snake_case for variables and functions
- [ ] PascalCase for classes
- [ ] Proper blank line usage
- [ ] Consistent naming conventions

### Error Handling & Return Codes
- [ ] Extractors return appropriate codes:
  - `100`: Success - joke extracted
  - `200`: No joke found
  - `500`: Failed to parse email
  - `501`: Other error during processing
- [ ] Primary script exits with `sys.exit(1)` on validation failures
- [ ] Logging uses appropriate levels:
  - `logging.debug()` for codes `100-199`
  - `logging.warning()` for codes `500-599`

### File Handling
- [ ] All email files processed with UTF-8 encoding
- [ ] Extractors use `tempfile.NamedTemporaryFile` with correct prefix and suffix
- [ ] No modification of original EML files
- [ ] All output files created atomically
- [ ] Extractors write to directory specified in second CLI argument
