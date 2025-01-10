### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import re
import datetime
import time
import json
from concurrent.futures import ThreadPoolExecutor

from script_logger import log_message
from api_caller import build_create_url, syntax_check
from utils import get_config
from meta_parser import parse_meta

__name__ = "rest_bulk_update.py"
__author__ = "Michel de Jong"
logfile = "rest_api_runner"

def parse_files(path):
    """Parse .conf and XML files into a dictionary."""
    params_dict = {}
    current_section = None
    tag = None
    formatted_data ={}

    try:
        if os.path.exists(path):
            # Get the filename
            filename = os.path.basename(path)

            with open(path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue

                    # Match section headers (stanzas) in .conf files
                    stanza_match = re.match(r'^\[(.*)\]$', line)
                    if stanza_match:
                        current_section = stanza_match.group(1)
                        params_dict[current_section] = {}

                    elif '=' in line:
                        if current_section:
                            key, value = map(str.strip, line.split('=', 1))
                            params_dict[current_section][key] = value

                            # Assign tag based on filename (exact match)
                            if filename == "savedsearches.conf":
                                tag = "savedsearches"
                                # Handle special case of changing key names to match API requirements
                                if "enableSched" in params_dict[current_section]:
                                    params_dict[current_section]['is_scheduled'] = params_dict[current_section].pop('enableSched')
                            elif filename == "macros.conf":
                                tag = "macros"
                            elif filename == "tags.conf":
                                tag = "tags"
                            elif filename == "eventtypes.conf":
                                tag = "eventtypes"
                            elif filename == "workflow_actions.conf":
                                tag = "workflow_actions"
                            elif filename == "datamodels.conf":
                                tag = "datamodels"
                                # Special handling for acceleration parameters
                                if key.startswith("acceleration."):
                                    # Remove "acceleration." prefix for JSON structure
                                    param_name = key.split("acceleration.", 1)[1]
                                    formatted_data.setdefault(current_section, {}).setdefault("acceleration", {})[param_name] = value
                            elif filename == "transforms.conf":
                                tag = "transforms"
                            elif filename == "collections.conf":
                                tag = "transforms"
                            elif filename == "props.conf":
                                # Special handling for props.conf
                                if 'EXTRACT' in key or 'REPORT' in key:
                                    tag = "props_extract"
                                elif 'EVAL' in key:
                                    tag = "props_eval"
                                elif 'FIELDALIAS' in key:
                                    tag = "props_fieldalias"
                                elif 'LOOKUP' in key:
                                    tag = "props_lookup"
                                elif 'rename' in key:
                                    tag = "props_sourcetype_rename"

    except Exception as e:
        log_message(logfile, f"Error parsing {path}: {e}", level="error")
    
    # Post-process acceleration data for API compatibility
    if tag == "datamodels":
        for stanza, data in formatted_data.items():
            if "acceleration" in data:
                # Convert acceleration dictionary to JSON string
                data["acceleration"] = json.dumps(data["acceleration"])

    return params_dict, tag

def collect_files(location):
    """Recursively collect relevant files from app/local directories and their app names."""
    files = []
    for app in os.listdir(location):
        app_path = os.path.join(location, app)
        if os.path.isdir(app_path):
            local_path = os.path.join(app_path, "local")
            if os.path.exists(local_path):
                for root, _, filenames in os.walk(local_path):
                    for filename in filenames:
                        if filename.endswith(('.conf', '.xml')):
                            # For XML files, determine the tag based on their location
                            if filename.endswith('.xml'):
                                if 'data/ui/view' in root:
                                    tag = 'views'
                                elif 'data/ui/panels' in root:
                                    tag = 'panels'
                                elif 'data/ui/nav' in root:
                                    tag = 'nav'
                            # Append a tuple (file_name, app_name, full_path, tag)
                            files.append((filename, app, root, tag))
    return files

def rest_bulk_create(args):
    try:
        # Read configuration values
        api_url_base, location, token, max_api_calls = get_config()

        # Record the start time
        start_time = datetime.datetime.now()
        
        if args.dummy is False:
            syntax_check(api_url_base)  

        log_message(logfile, f"API url: {api_url_base}", level="info") 

        delay_between_calls = 1.0 / max_api_calls  # 1 second divided by number of max API calls

        # Collect files
        files = collect_files(location)

        log_message(logfile, f"Collected {len(files)} files from {location}.", level="info")

        with ThreadPoolExecutor(max_workers=max_api_calls) as executor:
            futures = []
            for file_name, app_name, full_path, tag in files:
                # Parse and process each file
                file_path = os.path.join(location, app_name, "local", file_name)
                if file_name.endswith(".conf"):
                    parsed_data, tag = parse_files(file_path)
                    for stanza, params in parsed_data.items():
                        futures.append(
                            executor.submit(
                                build_create_url, api_url_base, token, args, file_name, stanza, params, app_name, tag
                            )
                        )
                        time.sleep(delay_between_calls)
                elif file_name.endswith(".xml"):
                    # Handle XML files (e.g., dashboards, panels, or navbars)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    futures.append(
                        executor.submit(
                            build_create_url, api_url_base, token, args, file_name, "eai:data", xml_content, app_name, tag
                        )
                    )
                    time.sleep(delay_between_calls)

            for future in futures:
                future.result()

        runtime = (datetime.datetime.now() - start_time).seconds
        print(f"Script completed in {runtime} seconds.")
        log_message(logfile, f"Script completed successfully in {runtime} seconds.", level="info")

    except Exception as e:
        log_message(logfile, f"Error in rest_bulk_create: {e}", level="error")