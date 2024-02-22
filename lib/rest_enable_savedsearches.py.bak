### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import sys
import getpass
import datetime

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message
from api_caller import build_enable_url, syntax_check

__name__ = "rest_enable_savedsearches.py"
__author__ = "Michel de Jong"

def process_searches(api_url, token, args, location, app_name, dir):
    savedsearches_path = os.path.join(location, app_name, dir, "savedsearches.conf")
    if os.path.exists(savedsearches_path):
        with open(savedsearches_path, "r") as f:
            inside_stanza = False  # Flag to track if inside a stanza
            stanza = None
            has_disabled = False # Flag to track if stanza has a disabled parameter

            for line in f:
                if args.debug:
                    log_message(__name__, f"{app_name}/{dir}: {line.strip()}", level="debug")
                if line.startswith("[") and line.endswith("]\n"):
                    if inside_stanza:
                        # Reached the end of the current stanza
                        # Check if "disabled" parameter was not found, and if not, process the stanza
                        if not has_disabled and dir=="default":
                            # No "disabled" parameter found, make an API call to enable stanza when in default directory
                            build_enable_url(api_url, token, args, app_name, stanza)
                        stanza = None
                        has_disabled = False
                    
                    stanza = line[1:-1]
                    line = line.strip()
                    inside_stanza = True
                elif inside_stanza:
                    if line.startswith("disabled = 0") or line.startswith("disabled=0"):
                        # "disabled = 0" is found, make an API call to enable the stanza
                        build_enable_url(api_url, token, args, app_name, stanza)
                        has_disabled = True
                    elif line.startswith("disabled = 1") or line.startswith("disabled=1"):
                        # "disabled = 1" is found, make an API call to disable the stanza
                        build_enable_url(api_url, token, args, app_name, stanza, enable=False)
                        has_disabled = True

            # Check the last stanza in the file
            if inside_stanza and not has_disabled and dir=="default":
                build_enable_url(api_url, token, args, app_name, stanza)

def rest_bulk_enable_savedsearches(args):
    try:
        # Get the location of the Splunk app location from user input
        location = input("Enter the location of the Splunk apps: \n")
        # Ask for API url and token from user input
        api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089): \n")
        token = getpass.getpass(prompt="Enter the authentication token: \n")
        # Record the start time
        start_time = datetime.datetime.now()
        syntax_check(api_url)
        log_message(__name__, f"API url: {api_url}", level="info")
        
        # Iterate over default and local directories of each app with savedsearches.conf
        for app_name in os.listdir(os.path.join(location)):
            process_searches(api_url, token, args, location, app_name, "default")
            process_searches(api_url, token, args, location, app_name, "local")

        # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")
        
        return
    
    except Exception as e:
        print(f"An error occurred: {e}")