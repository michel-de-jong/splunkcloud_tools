### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import re
import sys
import urllib.parse
import requests

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "api_caller.py"
__author__ = "Michel de Jong"
logfile = "rest_api_runner"

api_calls_count = 0

def make_api_call(api_url, app_name, encoded_stanza, headers, data):
    global api_calls_count
    api_calls_count += 1
    
    try:
        response = requests.post(api_url, headers=headers, data=data)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"#{api_calls_count} | API call successful")
            log_message(logfile, f"API call successful for {encoded_stanza} in {app_name}", level="info")
        else:
            print(f"#{api_calls_count} | API call failed, see error.log for details")
            log_message(logfile, f"API call failed for {encoded_stanza} in {app_name}. Status Code: {response.status_code}", level="error")
            log_message(logfile, f"Response Content: {response.text}", level="error")
            
    except requests.exceptions.RequestException as e:
        print(f"#{api_calls_count} | API call failed due to a network error: {e}")
        log_message(logfile, f"API call failed for {encoded_stanza} in {app_name}. Network error: {e}", level="error")
    except Exception as e:
        print(f"#{api_calls_count} | API call failed due to an unexpected error: {e}")
        log_message(logfile, f"API call failed for {encoded_stanza} in {app_name}. Unexpected error: {e}", level="error")

def dummy_api_call(api_url, app_name, encoded_stanza, headers, data):
    global api_calls_count
    api_calls_count += 1
    print(f"#{api_calls_count} | Dummy API call successful")
    log_message(logfile, f"Dummy run successful for {encoded_stanza} in {app_name}", level="info")

def build_create_url(api_url, token, args, app_name, stanza_name, savedsearch_params):
    if not savedsearch_params:
        log_message(logfile, f"Skipping saved search '{stanza_name}' in app '{app_name}' as no parameters found.", level="info")
        return
    encoded_stanza = urllib.parse.quote(stanza_name)
    api_call = f"{api_url}/servicesNS/nobody/{app_name}/saved/searches/{encoded_stanza}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = savedsearch_params  # Use all savedsearch_params dynamically

    if args.debug:
        log_message(logfile, f"--------------------------------------", level="debug")
        log_message(logfile, f"Processing saved search: {stanza_name}", level="debug")
        log_message(logfile, f"API URL: {api_call}", level="debug")
        # Remove comment below to enable header in debug logs
        # log_message(logfile, f"Headers: {headers}", level="debug")
        log_message(logfile, f"Data: {data}", level="debug")
    if args.dummy:
        dummy_api_call(api_call, app_name, encoded_stanza, headers, data)
    else:
        make_api_call(api_call, app_name, encoded_stanza, headers, data)

def build_enable_url(api_url, token, args, app_name, stanza_name, enable=True):
    encoded_stanza = urllib.parse.quote(stanza_name)
    api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"disabled": "0" if enable else "1"}

    if args.debug:
        log_message(logfile, f"--------------------------------------", level="debug")
        log_message(logfile, f"Processing saved search: {stanza_name}", level="debug")
        log_message(logfile, f"API URL: {api_call}", level="debug")
        # Remove comment below to enable header in debug logs
        # log_message(logfile, f"Headers: {headers}", level="debug")
        log_message(logfile, f"Data: {data}", level="debug")
    if args.dummy:
        dummy_api_call(api_call, app_name, encoded_stanza, headers, data)
    else:
        make_api_call(api_call, app_name, encoded_stanza, headers, data)

def syntax_check(api_url):
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
        
        return stackname

    except (ValueError, AttributeError) as e:
        # Handle URL parsing errors
        print(f"Error parsing API url: {e}")
        return None
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None