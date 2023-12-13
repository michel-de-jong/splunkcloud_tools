### DISCLAIMER
#
# THE SCRIPT IS NOT PERFECT
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import re
import getpass
import urllib.parse
import requests
import datetime
import argparse

__name__ = "rest_bulk_update_savedsearches.py"
__author__ = "Michel de Jong"

api_calls_count = 0

def make_api_call(api_url, app_name, encoded_stanza, headers, data):
    global api_calls_count
    api_calls_count += 1
    
    try:
        response = requests.post(api_url, headers=headers, data=data)
        
        if response.status_code == 200:
            print(f"#{api_calls_count} | API call successful")
            log_message(api_url, f"API call successful for {encoded_stanza} in {app_name}", level="info")
        else:
            print(f"#{api_calls_count} | API call failed, see error.log for details")
            log_message(api_url, f"API call failed for {encoded_stanza} in {app_name}. Status Code: {response.status_code}", level="error")
            log_message(api_url, f"Response Content: {response.text}", level="error")
            
    except requests.exceptions.RequestException as e:
        print(f"#{api_calls_count} | API call failed due to a network error: {e}")
        log_message(api_url, f"API call failed for {encoded_stanza} in {app_name}. Network error: {e}", level="error")

def dummy_api_call(api_url, app_name, encoded_stanza, headers, data):
    global api_calls_count
    api_calls_count += 1
    print(f"#{api_calls_count} | Dummy API call successful")
    log_message(api_url, f"Dummy API call successful for {encoded_stanza} in {app_name} with the following data: {data}", level="dummy")

def log_message(api_url, message, level):
    log_directory = create_log_directory(api_url)
    log_file = os.path.join(log_directory, f"{level}.log")

    with open(log_file, "a") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] [{level.upper()}] {message}\n")

def create_log_directory(api_url):
    try:
        # Check if api_url matches any of the expected patterns
        if re.match(r'^https?\:\/\/shc?\d+?\.', api_url):
            stackname = urllib.parse.urlparse(api_url).hostname.split('.')[0]+"_"+urllib.parse.urlparse(api_url).hostname.split('.')[1]
        elif re.match(r'^https?\:\/\/[a-z\-]+\.splunkcloud\.com', api_url):
            s = re.search(r'^https?\:\/\/([^\.]+)\.splunkcloud\.com', api_url)
            stackname = s.group(1)
        else:
            s = re.search(r'^https?\:\/\/([^\:]+)\:\d+', api_url)
            stackname = s.group(1)
        
        date = datetime.datetime.now().strftime("%Y%m%d")
        directory_name = f"run_{stackname}_{date}"
        
        # Attempt to create the directory, handling any potential errors
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        
        return directory_name

    except (ValueError, AttributeError) as e:
        # Handle URL parsing errors
        print(f"Error parsing API url: {e}")
        return None
    except OSError as e:
        # Handle directory creation errors
        print(f"Error creating directory: {e}")
        return None
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None

def build_url(api_url, token, args, app_name, stanza_name, enable=True):
    encoded_stanza = urllib.parse.quote(stanza_name)
    api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"disabled": "0" if enable else "1"}
    if args.debug:
        log_message(api_url, f"--------------------------------------", level="debug")
        log_message(api_url, f"Processing saved search: {stanza_name}", level="debug")
        log_message(api_url, f"API URL: {api_call}", level="debug")
        # Remove comment below to enable header in debug logs
        # log_message(api_url, f"Headers: {headers}", level="debug")
        log_message(api_url, f"Data: {data}", level="debug")
        log_message(api_url, f"--------------------------------------", level="debug")
    if args.dummy:
        dummy_api_call(api_call, app_name, encoded_stanza, headers, data)
    else:
        make_api_call(api_call, app_name, encoded_stanza, headers, data)

def process_searches(api_url, token, args, location, app_name, dir):
    savedsearches_path = os.path.join(location, app_name, dir, "savedsearches.conf")
    if os.path.exists(savedsearches_path):
        with open(savedsearches_path, "r") as f:
            inside_stanza = False  # Flag to track if inside a stanza
            stanza = None
            has_disabled = False # Flag to track if stanza has a disabled parameter

            for line in f:
                if args.debug:
                    log_message(api_url, f"{app_name}/{dir}: {line.strip()}", level="debug")
                if line.startswith("[") and line.endswith("]\n"):
                    if inside_stanza:
                        # Reached the end of the current stanza
                        # Check if "disabled" parameter was not found, and if not, process the stanza
                        if not has_disabled and dir=="default":
                            # No "disabled" parameter found, make an API call to enable stanza when in default directory
                            build_url(api_url, token, args, app_name, stanza)
                        stanza = None
                        has_disabled = False
                    
                    stanza = line[1:-1]
                    line = line.strip()
                    inside_stanza = True
                elif inside_stanza:
                    if line.startswith("disabled = 0") or line.startswith("disabled=0"):
                        # "disabled = 0" is found, make an API call to enable the stanza
                        build_url(api_url, token, args, app_name, stanza)
                        has_disabled = True
                    elif line.startswith("disabled = 1") or line.startswith("disabled=1"):
                        # "disabled = 1" is found, make an API call to disable the stanza
                        build_url(api_url, token, args, app_name, stanza, enable=False)
                        has_disabled = True

            # Check the last stanza in the file
            if inside_stanza and not has_disabled and dir=="default":
                build_url(api_url, token, args, app_name, stanza)

def main(args):
    try:
        # Get the location of the Splunk app location from user input
        location = input("Enter the location of the Splunk apps: \n")
        # Ask for API url and token from user input
        api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089, https://(es-)stackname.splunkcloud.com:8089, http(s)://anyhost:8089): \n")
        token = getpass.getpass(prompt="Enter the authentication token: \n")
        # Record the start time
        start_time = datetime.datetime.now()
        log_message(api_url, f"API url: {api_url}", level="info")
        
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
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "rest_bulk_update_savedsearches.py":
    parser = argparse.ArgumentParser(description="Script to update saved searches in Splunk apps")
    parser.add_argument("-debug", action="store_true", help="Enable debug mode, create an extra logfile with all debug logs")
    parser.add_argument("-dummy", action="store_true", help="Run in dummy mode, bypasses the actual API calls")
    args = parser.parse_args()

    main(args)
