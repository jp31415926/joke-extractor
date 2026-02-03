# orchestrator-blueprint.md

## Orchestrator Blueprint: Joke Extractor

For all steps verify that the step is correct, update the @docs/todos.md file and check all boxes for items that are complete. Use this to make sure all the steps are completed.

Phase 1: Environment & Test Data
Step 1: Project Scaffolding

    Action: Create project directories: extractors/, tests/, and jokes/. Initialize @joke-extract.py and @extractors/default.py as executable Python 3.11+ scripts with shebangs.

    Verification: Run `ls -R` and check `chmod +x` status on scripts.

Step 2: RFC-Compliant Test Fixtures

    Action: Create the following .eml files in @tests/ based on @docs/spec.md:

        valid_plain.eml: Subject present, From present, non-empty text/plain.

        valid_html.eml: Subject present, From present, non-empty text/html.

        empty_body.eml: text/plain exists but is empty.

        invalid_attachment.eml: Contains an application/pdf part.

        missing_from.eml: From: header is an empty string.

    Verification: Run a python one-liner to verify email.message_from_file loads each without crashing.

Phase 2: Extractor Development (extractors/default.py)
Step 3: Argument & Email Parsing

    Action: Implement CLI argument handling (2 args) and email.message_from_file parsing with UTF-8 enforcement.

    Verification: Execute @extractors/default.py @tests/valid_plain.eml ./jokes/ and verify exit code 0.

Step 4: MIME Priority Logic

    Action: Implement part scanning. Prioritize text/plain exactly; fallback to text/html; ignore others. Print 100 Success or 200 No joke found based on discovery.

    Verification: Verify valid_plain.eml prints 100 and empty_body.eml prints 200.

Step 5: Atomic File Writing

    Action: Use tempfile.NamedTemporaryFile with prefix="joke_" and suffix=".txt" to write content to output_dir.

    Verification: Ensure a file appears in jokes/ after running against valid_plain.eml.

Phase 3: Primary Script Development (joke-extract.py)
Step 6: Input Validation

    Action: Implement sys.exit(1) logic for: file readability, missing Subject, empty From, or any non-text attachments.

    Verification: Run @joke-extract.py @tests/invalid_attachment.eml; verify exit code is 1.

Step 7: Extractor Orchestration

    Action: Implement @extractors/ discovery (alphabetical), subprocess execution, and stdout capture.

    Verification: Run with logging set to DEBUG. Verify the log shows the captured 100 Success string.

Step 8: Return Code & Early Exit

    Action: Implement return code logic: Stop on 100-199, continue on 200-299, warn on 500-599. Exit 1 if no 100-199 is received.

    Verification: Run against valid_plain.eml (should exit 0) and empty_body.eml (should exit 1).

Phase 4: Final Integration
Step 9: End-to-End Testing

    Action: Create @tests/integration_test.py that invokes the full pipeline and asserts the existence of the joke file in jokes/.

    Verification: Run pytest @tests/ or python3 @tests/integration_test.py.

Step 10: Cleanup & Audit

    Action: Remove all print() statements. Ensure all logs use the logging module. Confirm UTF-8 compliance.

    Verification: grep -r "print(" . should return no results.