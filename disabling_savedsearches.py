### DISCLAIMER
#
# THE SCRIPT IS NOT PERFECT
# USE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import shutil
import sys
import logging

__name__ = "disabling_savedsearches.py"
__author__ = "Michel de Jong"

# Create a global logger
logger = logging.getLogger("script_logger")
logger.setLevel(logging.DEBUG)

# Function to process the savedsearches.conf file
def process_file(file_path, debug=False):
    try:
        # Read the savedsearches.conf file
        with open(file_path, "r") as f:
            lines = f.readlines()
            
        modified = False

        # Loop over the lines in the file
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # Check if the line starts a new stanza
            if line.startswith("[") and not line.startswith("[default]") and not line.endswith("\\"):
                stanza_name = line[1:-1]  # Extract the stanza name without brackets
                
                # Check if the stanza has a disabled statement
                has_disabled = False
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line.startswith("["):
                        break
                    if next_line.startswith("disabled ="):
                        has_disabled = True
                        # Check if the disabled statement is already false or 0
                        if "false" in next_line or "0" in next_line:
                            # Disable the stanza by changing the statement to "disabled = 1"
                            lines[j] = "disabled = 1\n"
                            modified = True
                            if debug:
                                logger.debug(f"DEBUG: Disabled Stanza '{stanza_name}' in {file_path}")
                        break
                    if next_line.startswith("search") or next_line.startswith("|"):
                        continue
                    
                # If the stanza doesn't have a disabled statement, add one
                if not has_disabled:
                    lines.insert(i+1, "disabled = 1\n")
                    modified = True
                    if debug:
                        logger.debug(f"DEBUG: Inserted 'disabled = 1' for Stanza '{stanza_name}' in {file_path}")

        # If changes were made, write the modified savedsearches.conf file
        if modified:
            with open(file_path, "w") as f:
                f.writelines(lines)
                if debug:
                    logger.debug(f"DEBUG: Modified {file_path}")
                else:
                    print(f"INFO: Disabled saved searches in {file_path}")

    except PermissionError:
        print(f"ERROR: Permission denied: {file_path}")

if __name__ == "disabling_savedsearches.py":
    # Parse command-line arguments
    args = sys.argv[1:]
    debug_mode = "-debug" in args

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
    shutil.copytree(apps_dir, disabled_ss_dir)
    
    if debug_mode:
        # Create the "_DEBUG" directory inside "apps_ss_disabled"
        logging_dir = os.path.join(disabled_ss_dir, "_DEBUG")
        os.makedirs(logging_dir, exist_ok=True)
        
        # Configure logfile for DEBUG logs
        log_filename = os.path.join(logging_dir, "debug.log")
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, format="%(asctime)s - %(levelname)s: %(message)s")

    # Loop over all directories in the apps_ss_disabled directory
    for app_name in os.listdir(disabled_ss_dir):
        app_dir = os.path.join(disabled_ss_dir, app_name)
        if os.path.isdir(app_dir):
            # Look for savedsearches.conf in the app/default directory
            savedsearches_conf_path = os.path.join(app_dir, "default", "savedsearches.conf")
            if os.path.isfile(savedsearches_conf_path):
                process_file(savedsearches_conf_path, debug=debug_mode)
            # Look for savedsearches.conf in the app/local directory
            savedsearches_conf_path = os.path.join(app_dir, "local", "savedsearches.conf")
            if os.path.isfile(savedsearches_conf_path):
                process_file(savedsearches_conf_path, debug=debug_mode)