### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os, sys
import getpass
import json

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "utils.py"
__author__ = "Michel de Jong"
logfile = "rest_api_runner"

def read_config_params():
    try:
        # Construct the path to configs.json
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../configs/configs.json")
        
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

def endpoint_mapping():
    """Load the endpoint_mapping.json file."""
    try:
        # Construct the path to endpoint_mapping.json
        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../configs/endpoint_configs.json")


        # Check if the file exists
        if not os.path.exists(json_path):
            log_message(logfile, f"File not found: {json_path}", level="error")
            return None

        # Load and parse the JSON file
        with open(json_path, "r", encoding="utf-8") as json_file:
            endpoint_mapping = json.load(json_file)
            log_message(logfile, "Successfully loaded endpoint_mapping.json", level="info")
            return endpoint_mapping

    except Exception as e:
        log_message(logfile, f"Error loading endpoint_mapping.json: {e}", level="error")
        return None

def ask_for_input(value, value_name, is_password=False):
    if value:
        return value
    else:
        if is_password:
            value = getpass.getpass(prompt=f">Enter {value_name}: \n")
        else:
            value = input(f"> Enter {value_name}: \n").strip()
    return value

def get_config():
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
                    api_url = ask_for_input("", "API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089)")
                if location == "":
                    location = ask_for_input("", "apps location")
                if token == "":
                    token = ask_for_input("", "authentication token", is_password=True)
        else:
            api_url = ask_for_input(api_url, "API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089)")
            location = ask_for_input(location, "apps location")
            token = ask_for_input(token, "authentication token", is_password=True)

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
        
        return api_url, location, token, max_api_calls
    
    except Exception as e:
        print(f"An error occurred: {e}")