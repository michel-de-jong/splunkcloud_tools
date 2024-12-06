### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os, re, sys
import datetime
import urllib.parse, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import threading

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "api_caller.py"
__author__ = "Michel de Jong"
logfile = "rest_api_runner"

# Global counters
success_counter = 0
failure_counter = 0
total_time = 0
api_calls_made = 0

# Lock for synchronizing log writing
log_lock = threading.Lock()

def make_api_call(api_url, app_name, stanza_name, headers, data):
    global success_counter, failure_counter, total_time, api_calls_made

    try:
        st = datetime.datetime.now()
        response = requests.post(api_url, headers=headers, data=data, verify=False)
        et = datetime.datetime.now()
        timetaken = (et - st).total_seconds()

        with log_lock:
            total_time += timetaken
            api_calls_made += 1
        
            if response.status_code in {200, 201}:
                success_counter += 1
                log_message(logfile, f"API call successful for {api_url}, '{stanza_name}' in {app_name}", level="info")
            else:
                failure_counter += 1
                log_message(logfile, f"API call failed for {api_url}, '{stanza_name}' in {app_name}. Status Code: {response.status_code}", level="error")
                log_message(logfile, f"Response Content: {response.text}", level="error")

        # Calculate and display counters with average time
        with log_lock:
            avg_time = total_time / api_calls_made if api_calls_made > 0 else 0
            # Print the current counters and average time on the same line
            print(f"\rAPI Calls - Success: {success_counter} | Failure: {failure_counter} (see error.log)| Avg Time: {avg_time:.4f}s", end="")

    except requests.exceptions.RequestException as e:
        with log_lock:
            failure_counter += 1
            api_calls_made += 1
            print(f"#{api_calls_made} | API call failed due to a network error: {e}")
            log_message(logfile, f"API call failed for {api_url}, '{stanza_name}' in {app_name}. Network error: {e}", level="error")
    except Exception as e:
        with log_lock:
            failure_counter += 1
            api_calls_made += 1
            print(f"#{api_calls_made} | API call failed due to an unexpected error: {e}")
            log_message(logfile, f"API call failed for {api_url}, '{stanza_name}' in {app_name}. Unexpected error: {e}", level="error")

def dummy_api_call(api_url, app_name, stanza_name, headers, data):
    global success_counter, failure_counter, total_time, api_calls_made
    with log_lock:
        success_counter += 1
        print(f"\rDUMMY API Calls - Success: {success_counter}")
        log_message(logfile, f"Dummy run successful for {stanza_name} in {app_name}. API-url: {api_url}", level="dummy")

def build_create_url(api_url, token, args, app_name, stanza_name, savedsearch_params):
    encoded_stanza = urllib.parse.quote(stanza_name)
    # Replace "/" with "%252F" in the encoded string
    encoded_stanza = encoded_stanza.replace("/", "%252F")
    api_call = f"{api_url}/servicesNS/nobody/{app_name}/saved/searches"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = savedsearch_params  # Use all savedsearch_params dynamically
    api_call_acl = f"{api_url}/servicesNS/nobody/{app_name}/saved/searches/{encoded_stanza}/acl"
    data_acl = {"owner": "Nobody", "sharing": "app"}

    with log_lock:
        if args.debug:
            log_message(logfile, f"--------------------------------------", level="debug")
            log_message(logfile, f"Processing saved search: {stanza_name}", level="debug")
            log_message(logfile, f"API URL: {api_call}", level="debug")
            log_message(logfile, f"Data: {data}", level="debug")

    if args.dummy:
        dummy_api_call(api_call, app_name, stanza_name, headers, data)
    else:
        make_api_call(api_call, app_name, stanza_name, headers, data)
        make_api_call(api_call_acl, app_name, stanza_name, headers, data_acl)

def build_enable_url(api_url, token, args, app_name, stanza_name, enabled):
    encoded_stanza = urllib.parse.quote(stanza_name)
    encoded_stanza = encoded_stanza.replace("/", "%252F")
    api_call = f"{api_url}/servicesNS/nobody/{app_name}/configs/conf-savedsearches/{encoded_stanza}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"disabled": "0" if enabled else "1"}

    with log_lock:
        if args.debug:
            log_message(logfile, f"--------------------------------------", level="debug")
            log_message(logfile, f"Processing saved search: {stanza_name}", level="debug")
            log_message(logfile, f"API URL: {api_call}", level="debug")
            log_message(logfile, f"Data: {data}", level="debug")
            
    if args.dummy:
        dummy_api_call(api_call, app_name, stanza_name, headers, data)
    else:
        make_api_call(api_call, app_name, stanza_name, headers, data)

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