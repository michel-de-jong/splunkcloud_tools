### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os, re, sys
import datetime, time
import getpass
import json
from concurrent.futures import ThreadPoolExecutor

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

def read_config_params():
    try:
        # Adjust the file path to configs.json
        config_path = os.path.join(os.path.dirname(__file__), '..', 'configs.json')
        
        # Ensure the file exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
        
        with open(config_path, 'r') as file:
            config = json.load(file)
            
            # Read max_api_calls from the config
            max_api_calls = config.get("max_api_calls_second", 10)
            
            # Read optional parameters (api_url, app_location, token)
            api_url = config.get("api_url", "")
            location = config.get("app_location", "")
            token = config.get("token", "")
            
            # Handle default and optional values
            if max_api_calls <= 0:
                raise ValueError("max_api_calls_second must be a positive integer.")
            
            return config_path, max_api_calls, api_url, location, token
    
    except FileNotFoundError as fnf_error:
        print(f"{fnf_error}. Using default values.")
        return 10, "", "", ""
    except json.JSONDecodeError as json_error:
        print(f"Error decoding JSON: {json_error}. Using default values.")
        return 10, "", "", ""
    except ValueError as ve:
        print(f"Invalid value for max_api_calls: {ve}. Using default values.")
        return 10, "", "", ""
    except Exception as e:
        print(f"Unexpected error: {e}. Using default values.")
        return 10, "", "", ""

def ask_for_input(value, prompt, value_name, is_password=False):
    if value:
        return value
    else:
        if is_password:
            value = getpass.getpass(prompt=f">Enter {value_name}: \n")
        else:
            value = input(f">Enter {value_name}: \n").strip()
    return value

def rest_bulk_update_savedsearches(args):
    try:
        # Read configuration values
        config_path, max_api_calls, api_url, location, token = read_config_params()
        
        # Ask for user input only if not pre-configured
        print(f"\nAPI URL: {api_url if api_url else 'Not provided by configs.json'}")
        print(f"App Location: {location if location else 'Not provided by configs.json'}")
        print(f"Token: {'******' if token else 'Not provided by configs.json'}")

        # Ask for confirmation after printing all values
        if api_url and location and token:
            correct = input(f"\nAre these values correct? (y/n): ").strip().lower()
            if correct != 'y':
                # If the user says no, re-ask for the incorrect parameters only
                if api_url == "":
                    api_url = ask_for_input("", "Enter the API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089)", "API url")
                if location == "":
                    location = ask_for_input("", "Enter the Splunk app location", "App location")
                if token == "":
                    token = ask_for_input("", "Enter the authentication token", "Token", is_password=True)
        else:
            api_url = ask_for_input(api_url, "Enter the API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089)", "API url")
            location = ask_for_input(location, "Enter the Splunk app location", "App location")
            token = ask_for_input(token, "Enter the authentication token", "Token", is_password=True)

        # Update configs.json for api_url and location, if changed
        try:
            if config_path and (api_url or location):
                with open(config_path, 'r') as file:
                    config = json.load(file)
                
                if config.get("api_url") != api_url:
                    config["api_url"] = api_url
                if config.get("app_location") != location:
                    config["app_location"] = location
                
                with open(config_path, 'w') as file:
                    json.dump(config, file, indent=4)
        except Exception as e:
            log_message(logfile, f"Error updating configs.json: {e}", level="error")

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
                    
                    if args.create:
                        futures.append(executor.submit(build_create_url, api_url, token, args, app_name, stanza_name, savedsearch_params))
                    
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
                    
                    if args.create:
                        savedsearch_params['name'] = stanza_name
                        futures.append(executor.submit(build_create_url, api_url, token, args, app_name, stanza_name, savedsearch_params))
                    
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