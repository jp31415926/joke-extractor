#!/usr/bin/env python3

import sys
import os
import email
import tempfile
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

###############################################
### You Make Me Laugh parser
###############################################
def parse_You_Make_Me_Laugh(text, subject):
    # Extract subject without the date part
    # Like this: "Acts 2:38 - August 26, 2010" -> "Acts 2:38"
    sub_parts = subject.split('-')
    subject = "".join(sub_parts[:-1]).strip()

    msg = []
    msg.append(text[0])

    # Split the text into lines
    lines = text[0].split('\n')
    
    # Find the bar line
    bar_index = None
    for i, line in enumerate(lines):
        if line.strip()[:10] == "__________":
            bar_index = i
            break
    
    if bar_index is None:
        return msg, subject
    
    # Start after the bar and skip 2 lines
    i = bar_index + 2
    if i >= len(lines):
        return msg, subject
    
    # Check for "Newsletters" and skip additional lines
    line_parts = lines[i].split(' ')
    if line_parts and line_parts[-1] == "Newsletters":
        i += 2
        if i >= len(lines):
            return msg, subject
    
    # Check if current line matches subject
    line = lines[i].strip()
    if line == subject:
        i += 1
        if i >= len(lines):
            return msg, subject
        line = lines[i].strip()
    
    # Collect content until we find the target string
    new_content = ""
    while i < len(lines) and line != "cybersalt.org/cleanlaugh":
        new_content += line + "\n\n"
        i += 1
        if i < len(lines):
            line = lines[i].strip()
        else:
            line = ""
    
    if new_content:
        msg[0] = new_content
    
    return msg, subject

###############################################
### Steve Sanderson parser
###############################################
def parse_Sanderson(text, subject):
    # Sunday Fun Stuff Joke List:  MORE COLD FLORIDA WEATHER
    # Steve does not provide subjects :( maybe we can make an ID come up with one
    subject = ""
    from_hdr = "Steve C Sanderson <aardvark@illinois.edu>"

    jokes = []
    joke_index = 0

    state = 0
    prev = '-=+=-'

    # Split the text into lines
    lines = text[0].split('\n')
    new_content = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match state:
            case 0: # waiting on start delimiter
                # logging.info(f"state0: {line}")
                if line[:10] == "**********":
                    state = 1
                    # logging.info("found **********")
                i += 1

            case 1: # skip blank lines, then find a line with a colon at the end.
                # logging.info(f"state1: {line}")
                if len(line) == 0:
                    # logging.info(f"found blank line state = 1")
                    i += 1
                elif line[-1:] == ':':
                    i += 1
                    # logging.info(f"found line with colon: {line}")
                    state = 2
                elif line == 'Steve Sanderson':
                    # reached the end
                    i = len(lines)
                    # logging.info(f"found end: {line}")
                    break
                else:
                    # logging.info(f"moving to state 3")
                    state = 3
            
            case 2: # skip blank line
                if len(line) == 0:
                    i += 1
                    # logging.info(f"found blank line state = 2")
                state = 3
            
            case 3: # get text until a line that starts with '[' and ends with ']'
                if len(line) and line[:1] == '[' and line[-1:] == ']':
                    # logging.info(f"found end of joke: {line}")
                    i += 1
                    if len(new_content) > 0:
                        jokes.append(new_content)
                        joke_index += 1
                    new_content = ""
                    state = 1
                else:
                    if len(line) == 0:
                        pass
                        # if len(prev) > 0:
                        #     new_content += "\n"
                    else:
                        new_content += line + "\n\n"
                    i += 1
                    prev = line
                    # logging.info(f"joke line: {line}")

    if len(jokes) == 0:
        jokes.append(text[0])

    return jokes, subject, from_hdr


def parse_email(file_path):
    """Parse an email file and return the email message object."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return email.message_from_file(file)
    except Exception as e:
        logging.error(f"Failed to parse email: {e}")
        print(f"502 Failed to parse email: {e}")
        sys.exit(1)

def cleanup_subject(subject):
    subject = subject.strip()
    
    # Define prefixes to remove (case insensitive)
    prefixes = ["re:", "fw:", "fwd:"]
    
    while True:
        original_length = len(subject)
        
        # Check each prefix
        for prefix in prefixes:
            if subject.lower().startswith(prefix):
                subject = subject[len(prefix):].strip()
                break  # Break after first match to avoid removing multiple prefixes in one iteration
        
        # If no changes were made, break out of loop
        if len(subject) == original_length:
            break
    
    return subject
        

def cleanup_body(text_content):
    # Split the text into lines
    lines = text_content.split('\n')

    # First pass: remove '>' characters from the beginning of lines
    for i in range(len(lines)):
        line = lines[i].strip()
        while True:
            # Strip the line
            line = line.strip()
            # Check if the first character is '>'
            if line and line[0] == '>':
                # Remove the first '>' character
                line = line[1:].strip()
            else:
                # No more '>' characters at the beginning, break out of nested loop
                lines[i] = line
                break

    # Second pass: replace multiple blank lines with single blank line
    i = 0
    prev = "."
    while i < len(lines):
        if lines[i] == '' and prev == '':
            # If there are more than one blank line, keep only one
            del lines[i]
        else:
            prev = lines[i]
            i += 1

    # Remove blank lines at the beginning and end
    # Remove leading blank lines
    while lines and lines[0].strip() == '':
        lines.pop(0)

    # Remove trailing blank lines
    while lines and lines[-1].strip() == '':
        lines.pop()

    # Combine the lines back into a string
    return '\n'.join(lines)    


def extract_text_content(email_message):
    """Extract text content from the email message."""
    # Scan through parts looking for text/plain part
    text = ""

    # First collect all text parts
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            payload = part.get_payload(decode=True)
            if payload:
                text_content = payload.decode('utf-8').strip()
                # Only include parts with content
                if text_content:
                    if text:
                        text += "-=+=-\n";
                    text += cleanup_body(text_content)

    a = []
    a.append(text)
    return a

def extract_html_content(email_message):
    """Extract HTML content from the email message."""
    # Scan through parts looking for text/plain part
    text = ""

    # First collect all text parts
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/html':
            payload = part.get_payload(decode=True)
            if payload:
                text_content = payload.decode('utf-8').strip()
                # Only include parts with content
                if text_content:
                    process = subprocess.run(
                        ["lynx", "-stdin", "-dump", "-nolist", "-hiddenlinks=ignore", "-nomargins", 
                         "-nonumbers", "-nounderline", "-width=1024", "-trim_blank_lines"],
                        input=text_content,
                        text=True,
                        capture_output=True
                    )
                    text_content = process.stdout
                    if text_content:
                        if text:
                            text += "-=+=-\n";
                        text += cleanup_body(text_content)

    a = []
    a.append(text)
    return a

def main():
    if len(sys.argv) != 3:
        print(f"500 Not enough arguments provided")
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
    text_content = extract_text_content(email_message)
    html_content = extract_html_content(email_message)
    if text_content == html_content:
        logging.info("Text and HTML are the same.")

    if text_content == html_content or len(text_content) > len(html_content):
        joke_content = text_content
        logging.info("Using Text version")
    else:
        joke_content = html_content
        logging.info("Using HTML version")

    if joke_content:
        # Get headers
        from_header = email_message.get('From', '')
        subject_header = cleanup_subject(email_message.get('Subject', ''))

        if (from_header == "You Make Me Laugh <Crosswalk@crosswalkmail.com>"):
            joke_content, subject_header = parse_You_Make_Me_Laugh(joke_content, subject_header)
        if ("aardvark@illinois.edu" in from_header):
            joke_content, subject_header, from_header = parse_Sanderson(joke_content, subject_header)

        for joke in joke_content:
            # Write to temporary file using the naming conventions
            with tempfile.NamedTemporaryFile(mode='w', prefix='joke_', suffix='.txt', dir=output_dir, delete=False) as tmp_file:
                # Write headers
                tmp_file.write(f"From: {from_header}\n")
                tmp_file.write(f"Subject: {subject_header}\n")
                tmp_file.write("\n")  # Blank line
                # Write joke content
                tmp_file.write(joke)
                # tmp_file_path = tmp_file.name
                
            # Move temp file to final location (for atomic write)
            # final_path = os.path.join(output_dir, os.path.basename(tmp_file_path))
            # os.rename(tmp_file_path, final_path)
            logging.info(f"Successfully extracted joke to {tmp_file.name}")
        print("100 Successfully extracted joke")
    else:
        logging.info("No joke content found")
        print("200 No joke found")

if __name__ == "__main__":
    main()
