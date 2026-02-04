#!/usr/bin/env python3

import sys
import os
import email
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_email(file_path):
    """Parse an email file and return the email message object."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return email.message_from_file(file)
    except Exception as e:
        logging.error(f"Failed to parse email: {e}")
        print(f"502 Failed to parse email: {e}")
        sys.exit(1)

def extract_joke_content(email_message):
    """Extract joke content from the email message."""
    # Scan through parts looking for text/plain first, then text/html, then others
    text_content = None
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            # Prioritize text/plain exactly 
            payload = part.get_payload(decode=True)
            if payload:
                text_content = payload.decode('utf-8')
                # Check if it's not empty
                if text_content.strip():
                    return text_content
        elif content_type == 'text/html' and text_content is None:
            # Fallback to text/html if we haven't found text/plain yet
            payload = part.get_payload(decode=True)
            if payload:
                text_content = payload.decode('utf-8')
    
    # Return the found content (which could be None)
    return text_content

def main():
    if len(sys.argv) != 3:
        logging.error("Usage: python3 default.py <email_file> <output_dir>")
        print(f"500 Usage: python3 default.py <email_file> <output_dir>")
        sys.exit(1)
        
    email_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Validate that email file exists
    if not os.path.exists(email_file):
        logging.error(f"Email file does not exist: {email_file}")
        print(f"501 Email file does not exist: {email_file}")
        sys.exit(1)
        
    # Parse the email
    email_message = parse_email(email_file)
    
    # Extract joke content
    joke_content = extract_joke_content(email_message)
    
    if joke_content:
        # Write to temporary file using the naming conventions
        with tempfile.NamedTemporaryFile(mode='w', prefix='joke_', suffix='.txt', dir=output_dir, delete=False) as tmp_file:
            tmp_file.write(joke_content)
            tmp_file_path = tmp_file.name
            
        # Move temp file to final location (for atomic write)
        final_path = os.path.join(output_dir, os.path.basename(tmp_file_path))
        os.rename(tmp_file_path, final_path)
        logging.info(f"Successfully extracted joke to {final_path}")
        print("100 Successfully extracted joke")
    else:
        logging.info("No joke content found")
        print("200 No joke found")

if __name__ == "__main__":
    main()
