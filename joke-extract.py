#!/usr/bin/env python3

import sys
import os
import email
import subprocess
import logging
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_email(file_path):
    """Parse an email file and return the email message object."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return email.message_from_file(file)
    except Exception as e:
        logging.error(f"Failed to parse email: {e}")
        sys.exit(5)

def validate_email(email_message):
    """Validate that email has required headers."""
    # Check if Subject exists
    if not email_message.get('Subject'):
        logging.error("Email missing Subject header")
        sys.exit(6)
        
    # Check if From exists and is not empty
    sender = email_message.get('From')
    if not sender or sender.strip() == '':
        logging.error("Email missing From header or From header is empty")
        sys.exit(7)
    
def get_extractor_scripts():
    """Find all extractor scripts in the extractors directory."""
    extractors_dir = 'extractors'
    if not os.path.exists(extractors_dir):
        logging.error("Extractors directory not found")
        sys.exit(2)
        
    scripts = []
    for filename in sorted(os.listdir(extractors_dir)):
        if filename.endswith('.py') and filename != '__init__.py':
            script_path = os.path.join(extractors_dir, filename)
            if os.access(script_path, os.X_OK):  # Check if executable
                scripts.append(script_path)
    return scripts

def run_extractor(extractor_script, email_file, output_dir):
    """Execute an extractor script and capture only the first line of stdout."""
    try:
        result = subprocess.run(
            [sys.executable, extractor_script, email_file, output_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Only return the first line of stdout
        first_line = result.stdout.strip().split('\n')[0] if result.stdout.strip() else ""
        
        # Extract return code from first line (should be 3-digit code at start)
        return_code = 0
        if first_line:
            try:
                return_code = int(first_line.split()[0])
            except (ValueError, IndexError):
                # If we can't parse the code, treat as error
                return_code = 599
                
        return return_code, first_line
    except subprocess.CalledProcessError as e:
        logging.error(f"Extractor failed with return code {e.returncode}: {e.stderr}")
        return e.returncode, e.stderr.strip()

def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python3 joke-extract.py <email_file>")
        sys.exit(1)
        
    email_file = sys.argv[1]
    
    if not os.path.exists(email_file):
        logging.error(f"Email file does not exist: {email_file}")
        sys.exit(3)
    
    # Parse the email
    email_message = parse_email(email_file)
    
    # Validate the email
    validate_email(email_message)
    
    # Get all extractor scripts
    scripts = get_extractor_scripts()
    
    if not scripts:
        logging.error("No executable extractor scripts found in extractors directory")
        sys.exit(4)
    
    # Create output directory if it doesn't exist
    output_dir = 'jokes'
    os.makedirs(output_dir, exist_ok=True)
    
    # Run each extractor until one succeeds
    for script in scripts:
        logging.info(f"Running extractor: {script}")
        return_code, output = run_extractor(script, email_file, output_dir)
        
        # Handle return codes according to spec
        if 100 <= return_code <= 199:
            # Success - stop processing
            logging.debug(f"Extractor {script} reported success (code {return_code})")
            return 0
        elif 200 <= return_code <= 299:
            # No joke found - continue to next extractor
            logging.info(f"Extractor {script} found no joke (code {return_code})")
            continue
        elif 500 <= return_code <= 599:
            # Error - warn but continue
            logging.warning(f"Extractor {script} reported error (code {return_code}): {output}")
            continue
        else:
            # Unexpected return code
            logging.warning(f"Extractor {script} returned unexpected code {return_code}: {output}")
            continue
    
    # If we get here, no extractor found a joke
    logging.info("No joke found in email")
    sys.exit(100)

if __name__ == "__main__":
    main()