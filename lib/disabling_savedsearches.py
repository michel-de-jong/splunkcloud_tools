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
        if args.debug:
            log_message(logfile, f"Processing file: {file_path}", level="debug")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            if args.debug:
                # Log all lines read from the file
                log_message(logfile, f"Lines read from {file_path}:", level="debug")
            for line in lines:
                log_message(logfile, line.strip(), level="debug")

            # Process each line
            updated_lines = []
            current_section = None
            stanza_params = {}
            for line in lines:
                line = line.strip()
                if args.debug:
                    log_message(logfile, f"Processing line: {line}", level="debug")
                if line.startswith('#'): # Skip comment lines
                    if args.debug:
                        log_message(logfile, "Skipping comment line", level="debug")
                        continue
                    updated_lines.append(line)
                    continue
                stanza_match = re.match(r'^\[(.*)\]$', line)
                if stanza_match:
                    if current_section:
                        # Ensure 'disabled' parameter is present with value '1' for each stanza
                        stanza_params['disabled'] = stanza_params.get('disabled', '1')
                        # Write stanza with updated parameters to the list of lines
                        updated_lines.append(f"[{current_section}]")
                        for key, value in stanza_params.items():
                            updated_lines.append(f"{key} = {value}")
                        updated_lines.append("")  # Add an empty line after the stanza
                        stanza_params.clear()  # Clear stanza parameters for the next stanza
                    current_section = stanza_match.group(1)
                    log_message(logfile, f"Found stanza: {current_section}", level="info")
                    if args.debug:
                        log_message(logfile, f"Found stanza: {current_section}", level="debug")
                elif '=' in line:
                    if current_section:
                        key, value = map(str.strip, line.split('=', 1))
                        if key == 'disabled':
                            if value != '1':
                                log_message(logfile, f"Changed 'disabled' value to '1' in stanza: {current_section}", level="info")
                                if args.debug:
                                    log_message(logfile, f"Changed 'disabled' value to '1' in stanza: {current_section}", level="debug")
                            else:
                                log_message(logfile, f"Added 'disabled = 1' to stanza: {current_section}", level="info")
                                if args.debug:
                                    log_message(logfile, f"Added 'disabled = 1' to stanza: {current_section}", level="debug")
                            value = '1'  # Ensure 'disabled' parameter is always '1'
                        stanza_params[key] = value

            # Ensure 'disabled' parameter is present with value '1' for the last stanza
            if current_section:
                stanza_params['disabled'] = stanza_params.get('disabled', '1')
                updated_lines.append(f"[{current_section}]")
                for key, value in stanza_params.items():
                    updated_lines.append(f"{key} = {value}")
                if args.debug:
                    log_message(logfile, f"Added 'disabled = 1' to stanza: {current_section}", level="debug")

            # Write back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(updated_lines))
            
            log_message(logfile, f"Successfully processed and updated {file_path}", level="info")
        else:
            log_message(logfile, f"File {file_path} does not exist.", level="error")
    except PermissionError:
        print(f"ERROR: Permission denied: {file_path}")
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