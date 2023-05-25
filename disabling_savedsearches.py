import os
import shutil

__name__ = "disabling_savedsearches.py"
__author__ = "Michel de Jong"

# Path to the directory containing Splunk apps
apps_dir = input("Enter the path to the directory containing Splunk apps: \n")

# Create the "apps_ss_disabled" directory to copy apps
disabled_ss_dir = os.path.join(os.path.dirname(apps_dir), "apps_ss_disabled")

def process_file(file_path):
    try:
        # Read the savedsearches.conf file
        with open(file_path, "r") as f:
            lines = f.readlines()
        # Loop over the lines in the file
        for i in range(len(lines)):
            line = lines[i].strip()
            # Check if the line starts a new stanza
            if line.startswith("["):
                # Check if the stanza has a disabled statement
                has_disabled = False
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line.startswith("["):
                        break
                    if next_line.startswith("disabled"):
                        has_disabled = True
                        # Check if the disabled statement is already false or 0
                        if "false" in next_line or "0" in next_line:
                            # Disable the stanza by changing the statement to "disabled = 1"
                            lines[j] = "disabled = 1\n"
                        break
                # If the stanza doesn't have a disabled statement, add one
                if not has_disabled:
                    lines.insert(i+1, "disabled = 1\n")
        # Write the modified savedsearches.conf file
        with open(file_path, "w") as f:
            f.writelines(lines)
            print(f"INFO: Disabled {file_path}")
    except PermissionError:
        print(f"ERROR: Permission denied: {file_path}")

# Copy the apps to apps_ss_disabled directory
while os.path.exists(disabled_ss_dir):
    decision = input(f"Destination directory {disabled_ss_dir} already exist. Proceed and overwrite? (y/n): \n")
    if decision.lower() == "y":
        shutil.rmtree(disabled_ss_dir)
        break
    elif decision.lower() == "n":
        print("Exiting the script")
        exit(0)
shutil.copytree(apps_dir, disabled_ss_dir)

# Loop over all directories in the apps_ss_disabled directory
for app_name in os.listdir(disabled_ss_dir):
    app_dir = os.path.join(disabled_ss_dir, app_name)
    if os.path.isdir(app_dir):
        # Look for savedsearches.conf in the app/default directory
        savedsearches_conf_path = os.path.join(app_dir, "default", "savedsearches.conf")
        if os.path.isfile(savedsearches_conf_path):
            process_file(savedsearches_conf_path)
        # Look for savedsearches.conf in the app/local directory
        savedsearches_conf_path = os.path.join(app_dir, "local", "savedsearches.conf")
        if os.path.isfile(savedsearches_conf_path):
            process_file(savedsearches_conf_path)