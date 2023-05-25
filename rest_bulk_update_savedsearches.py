import os
import urllib.parse
import requests

__name__ = "rest_bulk_update_savedsearches.py"
__author__ = "Michel de Jong"

# Get the location of the Splunk app location from user input
location = input("Enter the location of the Splunk apps: ")

# Ask for API url and token from user input
api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089): ")
token = input("Enter the authentication token: ")

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
                        response = requests.post(api_call, headers=headers, data=data)
                        if response.status_code != 200:
                            print(f"API call failed for {stanza} in {app_name}")
                        if response.status_code == 200:
                            print(f"API call successful for {stanza} in {app_name}")

# Iterate over local directories of each app with savedsearches.conf
for app_name in os.listdir(os.path.join(location)):
    savedsearches_path = os.path.join(location, app_name, "local", "savedsearches.conf")
    if os.path.exists(savedsearches_path):
        with open(savedsearches_path, "r") as f:
            for line in f:
                if line.startswith("[") and line.endswith("]\n"):
                    stanza = line.strip()[1:-1]
                    if "disabled=0" in line or "disabled = 0" in line or "disabled=false" in line or "disabled = false" in line:
                        encoded_stanza = urllib.parse.quote(stanza)
                        # Make API call to enable the saved search
                        api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                        headers = {"Authorization": f"Bearer {token}"}
                        data = {"disabled": "0"}
                        response = requests.post(api_call, headers=headers, data=data)
                        if response.status_code != 200:
                            print(f"API call failed for {stanza} in {app_name}")
                        if response.status_code == 200:
                            print(f"API call successful for {stanza} in {app_name}")
                    elif "disabled=1" in line or "disabled = 1" in line or "disabled=true" in line or "disabled = true" in line:
                        encoded_stanza = urllib.parse.quote(stanza)
                        # Make API call to enable the saved search
                        api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
                        headers = {"Authorization": f"Bearer {token}"}
                        data = {"disabled": "1"}
                        response = requests.post(api_call, headers=headers, data=data)
                        if response.status_code != 200:
                            print(f"API call failed for {stanza} in {app_name}")
                        if response.status_code == 200:
                            print(f"API call successful for {stanza} in {app_name}")