### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os, re, sys
import datetime, time
from concurrent.futures import ThreadPoolExecutor

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message
from api_caller import build_enable_url, syntax_check
from utils import get_config

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
                    if line.startswith('#'): # Skip comment lines
                        continue
                    stanza_match = re.match(r'^\[(.*)\]$', line)
                    if stanza_match:
                        current_section = stanza_match.group(1)
                        params_dict[current_section] = {}
                    elif '=' in line:
                        if current_section:
                            kv_pair = line.split('=', 1)
                            if len(kv_pair) == 2:
                                key, value = map(str.strip, kv_pair)
                                params_dict[current_section][key] = value
                                # Change key name to match Splunk REST API required values
                                if "enableSched" in params_dict[current_section]:
                                    params_dict[current_section]['is_scheduled'] = params_dict[current_section].pop('enableSched')
    except Exception as e:
        log_message(logfile, f"Error parsing {savedsearches_path}: {e}", level="error")
    return params_dict

def rest_bulk_update_savedsearches(args):
    try:
        api_url, location, token, max_api_calls = get_config()
        # Record the start time
        start_time = datetime.datetime.now()
        
        if args.dummy is False:
            syntax_check(api_url)  

        log_message(logfile, f"API url: {api_url}", level="info") 

        delay_between_calls = 1.0 / max_api_calls  # 1 second divided by number of max API calls

        # Create a thread pool for making API calls
        with ThreadPoolExecutor(max_workers=max_api_calls) as executor:
            futures = []
            for app_name in os.listdir(os.path.join(location)):
                savedsearches_default_path = os.path.join(location, app_name, "default", "savedsearches.conf")
                savedsearches_data = parse_searches(savedsearches_default_path)
                # Dictionary to store 'disabled' values for each stanza from the default
                default_disabled = {}

                for stanza_name, savedsearch_params in savedsearches_data.items():
                    if not savedsearch_params:
                        log_message(logfile, f"Skipping default saved search '{stanza_name}' in app '{app_name}' as no parameters found.", level="info")
                        continue
                    
                    # Store the 'disabled' value from default configuration
                    disabled_value = savedsearch_params.get("disabled", None)
                    if disabled_value is not None:
                        disabled_value = disabled_value.lower()
                    default_disabled[stanza_name] = disabled_value

                    if args.enable:
                        if disabled_value == "0" or disabled_value == "false" or disabled_value is None:
                            futures.append(executor.submit(time.sleep, delay_between_calls))
                            futures.append(executor.submit(build_enable_url, api_url, token, args, app_name, stanza_name, True))
                        if disabled_value == "1" or disabled_value == "true":
                            futures.append(executor.submit(time.sleep, delay_between_calls))
                            futures.append(executor.submit(build_enable_url, api_url, token, args, app_name, stanza_name, False))

                savedsearches_local_path = os.path.join(location, app_name, "local", "savedsearches.conf")
                savedsearches_data = parse_searches(savedsearches_local_path)
                for stanza_name, savedsearch_params in savedsearches_data.items():
                    if not savedsearch_params:
                        log_message(logfile, f"Skipping local saved search '{stanza_name}' in app '{app_name}' as no parameters found.", level="info")
                        continue
                    
                    if args.enable:
                        # Check if the stanza exists in default configuration
                        disabled_value = savedsearch_params.get("disabled", None)
                        if disabled_value is None and stanza_name in default_disabled:
                            disabled_value = default_disabled[stanza_name].lower()
                        
                        if disabled_value == "0" or disabled_value == "false" or disabled_value is None:
                            futures.append(executor.submit(time.sleep, delay_between_calls))
                            futures.append(executor.submit(build_enable_url, api_url, token, args, app_name, stanza_name, True))
                        if disabled_value == "1" or disabled_value == "true":
                            futures.append(executor.submit(time.sleep, delay_between_calls))
                            futures.append(executor.submit(build_enable_url, api_url, token, args, app_name, stanza_name, False))

            # Wait for all futures to complete
            for future in futures:
                future.result()

        # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")

        return

    except Exception as e:
        print(f"An error occurred: {e}")