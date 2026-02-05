#!/usr/bin/env python3

import os
import sys
import tempfile
import subprocess

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extraction():
    """Test that joke extraction works correctly."""
    
    # Create test email files
    test_email_content = """Return-Path: <sender@example.com>
Received: by 10.10.10.10 with SMTP id abc123;
        Mon, 1 Jan 2023 01:00:00 -0800 (PST)
From: Sender Name <sender@example.com>
To: Recipient Name <recipient@example.com>
Subject: Test Joke Email
Date: Mon, 1 Jan 2023 01:00:00 -0800
Message-ID: <1234567890@example.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!
"""
    
    # Write test email to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(test_email_content)
        email_file = f.name
    
    try:
        # Run the main script
        result = subprocess.run([
            sys.executable, 'joke-extract.py', email_file
        ], capture_output=True, text=True, cwd='.')
        
        print("Exit code:", result.returncode)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        # Check if joke file was created
        if os.path.exists('jokes'):
            joke_files = os.listdir('jokes')
            if joke_files:
                print("Files created in jokes/:", joke_files)
                # Check content
                with open(os.path.join('jokes', joke_files[0]), 'r') as f:
                    content = f.read()
                    print("Content of joke file:", content)
        
        print("Test completed")
        
    finally:
        # Cleanup
        os.unlink(email_file)
        if os.path.exists('jokes'):
            for f in os.listdir('jokes'):
                os.unlink(os.path.join('jokes', f))
            os.rmdir('jokes')

if __name__ == "__main__":
    test_extraction()