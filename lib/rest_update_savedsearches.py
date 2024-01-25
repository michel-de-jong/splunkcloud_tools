### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import sys
import datetime
import getpass

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message
from api_caller import build_create_url, build_enable_url, syntax_check

__name__ = "rest_enable_savedsearches.py"
__author__ = "Michel de Jong"
logfile = "rest_api_runner"

def parse_searches(savedsearches_path):
    params_dict = {}
    current_section = None

    try:
        if os.path.exists(savedsearches_path):
            with open(savedsearches_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        params_dict[current_section] = {}
                    elif '=' in line:
                        if current_section:
                            key, value = map(str.strip, line.split('=', 1))
                            params_dict[current_section][key] = value
                            params_dict[current_section]['sharing'] = 'app'
    except Exception as e:
        log_message(logfile, f"Error parsing {savedsearches_path}: {e}", level="error")

    return params_dict

def rest_bulk_update_savedsearches(args):
    try:
        # Get the location of the Splunk app location from user input
        location = input("Enter the location of the Splunk apps: \n")
        # Ask for API url and token from user input
        api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089): \n")
        token = getpass.getpass(prompt="Enter the authentication token: \n")
        # Record the start time
        start_time = datetime.datetime.now()
        if args.dummy is False:
            syntax_check(api_url)
        log_message(logfile, f"API url: {api_url}", level="info")

        # Iterate over default and local directories of each app with savedsearches.conf
        for app_name in os.listdir(os.path.join(location)):
            savedsearches_default_path = os.path.join(location, app_name, "default", "savedsearches.conf")
            savedsearches_data = parse_searches(savedsearches_default_path)
            for stanza_name, savedsearch_params in savedsearches_data.items():
                if not savedsearch_params:
                    log_message(logfile, f"Skipping saved search '{stanza_name}' in app '{app_name}' as no parameters found.", level="info")
                    return
                if args.create:
                    build_create_url(api_url, token, args, app_name, stanza_name, savedsearches_data)
                if args.enable:
                    # Check if the "disabled" key exists in savedsearch_params
                    disabled_value = savedsearch_params.get("disabled", None)
                    if disabled_value is not None:
                        # Convert disabled_value to lowercase
                        disabled_value = disabled_value.lower()
                    if disabled_value == "0" or disabled_value == "false" or disabled_value == None:
                        build_enable_url(api_url, token, args, app_name, stanza_name)
                    if disabled_value == "1" or disabled_value == "true":
                        build_enable_url(api_url, token, args, app_name, stanza_name, enable=False)

            savedsearches_local_path = os.path.join(location, app_name, "local", "savedsearches.conf")
            parse_searches(savedsearches_local_path)
            for stanza_name, savedsearch_params in savedsearches_data.items():
                if args.create:
                    build_create_url(api_url, token, args, app_name, stanza_name, savedsearches_data)
                if args.enable:
                    # Check if the "disabled" key exists in savedsearch_params
                    disabled_value = savedsearch_params.get("disabled", None)
                    if disabled_value is not None:
                        # Convert disabled_value to lowercase
                        disabled_value = disabled_value.lower()
                    if disabled_value == "0" or disabled_value == "false":
                        build_enable_url(api_url, token, args, app_name, stanza_name)
                    if disabled_value == "1" or disabled_value == "true":
                        build_enable_url(api_url, token, args, app_name, stanza_name, enable=False)

        # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")

        return
    
    except Exception as e:
        print(f"An error occurred: {e}")