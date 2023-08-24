### DISCLAIMER
#
### USE SCRIPT AT YOUR OWN RISK

import os
import urllib.parse
import requests
import datetime
import argparse

__name__ = "rest_bulk_update_savedsearches.py"
__author__ = "Michel de Jong"

api_calls_count = 0

def make_api_call(api_url, app_name, encoded_stanza, headers, data):
    response = requests.post(api_url, headers=headers, data=data)
    global api_calls_count
    api_calls_count += 1
    if response.status_code == 200:
        print(f"#{api_calls_count} | API call successful")
        log_message(api_url, f"API call successful for {encoded_stanza} in {app_name}", level="info")
    else:
        print(f"#{api_calls_count} | API call failed, see error.log for details")
        log_message(api_url, f"API call failed for {encoded_stanza} in {app_name}. Status Code: {response.status_code}", level="error")
        log_message(api_url, f"Response Content: {response.text}", level="error")

def log_message(api_url, message, level):
    log_directory = create_log_directory(api_url)
    log_file = os.path.join(log_directory, f"{level}.log")

    with open(log_file, "a") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] [{level.upper()}] {message}\n")

def create_log_directory(api_url):
    stackname = urllib.parse.urlparse(api_url).hostname.split('.')[0]+"_"+urllib.parse.urlparse(api_url).hostname.split('.')[1]
    date = datetime.datetime.now().strftime("%Y%m%d")
    directory_name = f"run_{stackname}_{date}"
    
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    return directory_name

def main(args):
    # Get the location of the Splunk app location from user input
    location = input("Enter the location of the Splunk apps: ")

    # Ask for API url and token from user input
    api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089): ")
    token = input("Enter the authentication token: ")

    # Record the start time
    start_time = datetime.datetime.now()

    # Iterate over default directories of each app with savedsearches.conf
    for app_name in os.listdir(os.path.join(location)):
        savedsearches_path = os.path.join(location, app_name, "default", "savedsearches.conf")
        if os.path.exists(savedsearches_path):
            with open(savedsearches_path, "r") as f:
                for line in f:
                    if line.startswith("[") and line.endswith("]\n"):
                        stanza = line.strip()[1:-1]
                        if "disabled=0" in line or "disabled = 0" in line or "disabled=false" in line or "disabled = false" in line or "disabled" not in line:
                            encoded_stanza = urllib.parse.quote(stanza)
                            # Make API call to enable the saved search
                            api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                            headers = {"Authorization": f"Bearer {token}"}
                            data = {"disabled": "0"}
                            if args.debug:
                                log_message(api_url, "Processing saved search:", level="debug")
                                log_message(api_url, f"API URL: {api_call}", level="debug")
                                # Comment out header because of security reasons
                                # log_message(api_url, f"Headers: {headers}", level="debug")
                                log_message(api_url, f"Data: {data}", level="debug")
                            make_api_call(api_call, app_name, encoded_stanza, headers, data)

                        elif "disabled=1" in line or "disabled = 1" in line or "disabled=true" in line or "disabled = true" in line:
                            api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                            headers = {"Authorization": f"Bearer {token}"}
                            data = {"disabled": "1"}
                            if args.debug:
                                log_message(api_url, "Processing saved search:", level="debug")
                                log_message(api_url, f"API URL: {api_call}", level="debug")
                                # Comment out header because of security reasons
                                # log_message(api_url, f"Headers: {headers}", level="debug")
                                log_message(api_url, f"Data: {data}", level="debug")
                            make_api_call(api_call, app_name, encoded_stanza, headers, data)


    # Iterate over local directories of each app with savedsearches.conf
    for app_name in os.listdir(os.path.join(location)):
        savedsearches_path = os.path.join(location, app_name, "local", "savedsearches.conf")
        if os.path.exists(savedsearches_path):
            with open(savedsearches_path, "r") as f:
                for line in f:
                    if line.startswith("[") and line.endswith("]\n"):
                        stanza = line.strip()[1:-1]
                        encoded_stanza = urllib.parse.quote(stanza)
                        
                        if "disabled" in line or "disabled = 0" in line or "disabled=false" in line or "disabled = false" in line:
                            api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                            headers = {"Authorization": f"Bearer {token}"}
                            data = {"disabled": "0"}
                            if args.debug:
                                log_message(api_url, "Processing saved search:", level="debug")
                                log_message(api_url, f"API URL: {api_call}", level="debug")
                                # Comment out header because of security reasons
                                # log_message(api_url, f"Headers: {headers}", level="debug")
                                log_message(api_url, f"Data: {data}", level="debug")
                            make_api_call(api_call, app_name, encoded_stanza, headers, data)
                        
                        elif "disabled=1" in line or "disabled = 1" in line or "disabled=true" in line or "disabled = true" in line:
                            api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                            headers = {"Authorization": f"Bearer {token}"}
                            data = {"disabled": "1"}
                            if args.debug:
                                log_message(api_url, "Processing saved search:", level="debug")
                                log_message(api_url, f"API URL: {api_call}", level="debug")
                                # Comment out header because of security reasons
                                # log_message(api_url, f"Headers: {headers}", level="debug")
                                log_message(api_url, f"Data: {data}", level="debug")
                            make_api_call(api_call, app_name, encoded_stanza, headers, data)

    # Calculate the runtime
    end_time = datetime.datetime.now()
    runtime = (end_time - start_time).seconds

    # Display the runtime notification
    print(f"Script completed in {runtime} seconds.")
    print(f"Logfiles are created in the working directory of the script")

if __name__ == "rest_bulk_update_savedsearches.py":
    parser = argparse.ArgumentParser(description="Script to update saved searches in Splunk apps")
    parser.add_argument("-debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    main(args)
