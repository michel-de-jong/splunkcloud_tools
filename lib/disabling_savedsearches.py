### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import re
import sys
import shutil
import datetime

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "disabling_savedsearches.py"
__author__ = "Michel de Jong"
logfile = "disabling_savedsearches"

def process_file(file_path, args):
    try:
        log_message(logfile, f"Processing file: {file_path}", level="info")
        if not os.path.exists(file_path):
            log_message(logfile, f"File {file_path} does not exist.", level="error")
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if args.debug:
            log_message(logfile, f"Lines read from {file_path}: {lines}", level="debug")

        updated_lines = []
        current_stanza = None
        stanza_lines = []
        in_multiline_value = False

        for line in lines:
            stripped_line = line.rstrip()

            # Check for comments or blank lines
            if not stripped_line or stripped_line.startswith('#'):
                if in_multiline_value:
                    stanza_lines[-1] += f"\n{line.rstrip()}"  # Preserve within multiline values
                else:
                    updated_lines.append(line)
                continue

            # Detect if the line starts a new stanza (strict rule: no spaces inside brackets)
            stanza_match = re.match(r'^\[([^\[\]\s]+)\]$', stripped_line)
            if stanza_match and not in_multiline_value:
                # Finalize the previous stanza, if any
                if current_stanza:
                    # Ensure 'disabled = 1' is the first parameter in the stanza
                    updated_lines.append(f"[{current_stanza}]")
                    if not any(l.strip().startswith('disabled =') for l in stanza_lines):
                        updated_lines.append("disabled = 1")
                    updated_lines.extend(stanza_lines)
                    updated_lines.append("")  # Blank line between stanzas
                    stanza_lines = []

                # Start processing the new stanza
                current_stanza = stanza_match.group(1)
                log_message(logfile, f"Found stanza: {current_stanza}", level="info")
                continue

            # Handle multiline values (e.g., search = ...)
            if in_multiline_value:
                stanza_lines[-1] += f"\n{line.rstrip()}"  # Append to the previous parameter
                if not stripped_line.endswith('\\'):  # Multiline ends without a backslash
                    in_multiline_value = False
                continue

            # Detect a multiline value starting
            if '=' in stripped_line and stripped_line.endswith('\\'):
                stanza_lines.append(line.rstrip())  # Start of a multiline value
                in_multiline_value = True
                continue

            # Regular key-value pair within a stanza
            if '=' in stripped_line:
                stanza_lines.append(line.rstrip())
                continue

        # Finalize the last stanza
        if current_stanza:
            updated_lines.append(f"[{current_stanza}]")
            if not any(l.strip().startswith('disabled =') for l in stanza_lines):
                updated_lines.append("disabled = 1")
            updated_lines.extend(stanza_lines)

        # Write back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(updated_lines).strip() + '\n')  # Ensure proper final newline

        log_message(logfile, f"Successfully processed and updated {file_path}", level="info")

    except PermissionError:
        log_message(logfile, f"Permission denied: {file_path}", level="error")
    except Exception as e:
        log_message(logfile, f"Error processing {file_path}: {e}", level="error")





def disabling_savedsearches(args):
    try:
        # Path to the directory containing Splunk apps
        apps_dir = input("Enter the path to the directory containing Splunk apps: \n")

        # Create the "apps_ss_disabled" directory to copy apps
        disabled_ss_dir = os.path.join(os.path.dirname(apps_dir), "apps_ss_disabled")

        # Copy the apps to apps_ss_disabled directory
        if os.path.exists(disabled_ss_dir):
            decision = input(f"Destination directory {disabled_ss_dir} already exists. Proceed and overwrite? (y/n): \n")
            if decision.lower() == "y":
                shutil.rmtree(disabled_ss_dir)
            else:
                print("Exiting the script")
                exit(0)
                
        print(f"Copying the apps directory to {disabled_ss_dir}")
        start_time = datetime.datetime.now()
        shutil.copytree(apps_dir, disabled_ss_dir)

        # Loop over all directories in the apps_ss_disabled directory
        for app_name in os.listdir(disabled_ss_dir):
            app_dir = os.path.join(disabled_ss_dir, app_name)
            if os.path.isdir(app_dir):
                # Look for savedsearches.conf in the app/default directory
                savedsearches_conf_path = os.path.join(app_dir, "default", "savedsearches.conf")
                if os.path.isfile(savedsearches_conf_path):
                    process_file(savedsearches_conf_path, args)
                # Look for savedsearches.conf in the app/local directory
                savedsearches_conf_path = os.path.join(app_dir, "local", "savedsearches.conf")
                if os.path.isfile(savedsearches_conf_path):
                    process_file(savedsearches_conf_path, args)
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")
        
        return