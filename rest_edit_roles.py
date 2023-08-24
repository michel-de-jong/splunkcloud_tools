import os
import urllib.parse
import requests

__name__ = "rest_edit_roles.py"
__author__ = "Michel de Jong"

# Get the location of the Splunk app location from user input
location = input("Enter the location of the Splunk apps: ")

# Ask for input from user input
api_url = input("Enter the API url (https://shc1.stackname.splunkcloud.com:8089): ")
token = input("Enter the authentication token: ")
role = input("Enter role to edit")
imported = ("Enter imported role")


#api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
api_call = f"{api_url}/services/authorization/roles/user"
headers = {"Authorization": f"Bearer {token}"}
data = {"imported_roles": "everyone_adhoc"}
response = requests.post(api_call, headers=headers, data=data)
if response.status_code != 200:
    print(f"API call failed")
if response.status_code == 200:
    print(f"API call successful")