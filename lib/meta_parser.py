import os
import configparser
import urllib.parse
from collections import defaultdict
import json

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "meta_parser.py"
__author__ = "Michel de Jong"
logfile = "meta_parser"

# # Mapping of .conf files and knowledge objects to their respective Splunk REST API endpoints
# ENDPOINT_MAPPING = {
#     "props": "configs/conf-props",
#     "savedsearches": "configs/conf-savedsearches",
#     "macros": "configs/conf-macros",
#     "views": "data/ui/views",
#     "field_extractions": "data/props/extractions",
#     "field_transformations": "data/props/transforms",
#     "eventtypes": "configs/conf-eventtypes",
#     "tags": "configs/conf-tags",
#     "workflow_actions": "data/ui/workflow-actions",
#     "nav_menus": "data/ui/nav",
#     "panels": "data/ui/panels",
# }

def determine_scope(raw_stanza):
    """
    Determine the scope of the stanza:
    - App-wide: `[]`
    - Conf-wide: `[props]`
    - Object-specific: `[props/object_name]`
    """
    if raw_stanza == "":
        return "app", None, None
    parts = raw_stanza.split("/", 1)
    if len(parts) == 1:
        return "conf_file", parts[0], None
    return "object", parts[0], parts[1]

def parse_meta_with_configparser(file_path):
    """
    Parse metadata from a file and prepare it for API calls.
    """
    config = configparser.ConfigParser(strict=False, interpolation=None)
    config.read(file_path)

    parsed_data = []
    for section in config.sections():
        raw_stanza = urllib.parse.unquote(section)
        scope, conf_file, object_name = determine_scope(raw_stanza)

        # Determine the API endpoint
        api_endpoint = ENDPOINT_MAPPING.get(conf_file, None)
        if not api_endpoint:
            continue  # Skip unknown object types

        # Prepare the data dictionary for API calls
        parameters = defaultdict(dict)
        for key, value in config.items(section):
            # Split keys like `perms.read` into nested dictionaries
            if "." in key:
                top_key, sub_key = key.split(".", 1)
                parameters[top_key][sub_key] = value
            else:
                parameters[key] = value

        api_data = {
            "stanza_name": raw_stanza,
            "scope": scope,
            "api_endpoint": api_endpoint,
            "object_name": object_name,
            "parameters": dict(parameters),
        }
        parsed_data.append(api_data)

    return parsed_data

def prepare_api_calls(parsed_data, api_url, token, app_name):
    """
    Prepare API calls for the `api_caller.py` script.
    """
    api_calls = []

    for data in parsed_data:
        stanza_name = data["stanza_name"]
        scope = data["scope"]
        api_endpoint = data["api_endpoint"]
        object_name = data["object_name"]
        parameters = data["parameters"]

        # Build the API URL
        if scope == "object":
            encoded_stanza = urllib.parse.quote(object_name).replace("/", "%252F")
            api_url_full = f"{api_url}/{api_endpoint}/{encoded_stanza}/acl"
        elif scope == "conf_file":
            api_url_full = f"{api_url}/{api_endpoint}"
        elif scope == "app":
            # Special case for `[]` stanza: Apply metadata to the entire app
            api_url_full = f"{api_url}/{api_endpoint}"
        else:
            continue  # Skip if no valid scopea

        # Prepare the payload
        payload = {}
        if "access" in parameters:
            access = parameters["access"]
            if "read" in access:
                payload["perms.read"] = access["read"]
            if "write" in access:
                payload["perms.write"] = access["write"]
        if "owner" in parameters:
            payload["owner"] = parameters["owner"]
        if "export" in parameters:
            sharing = "global" if parameters["export"] == "system" else "app"
            payload["sharing"] = sharing

        # Add to API calls list
        api_calls.append({
            "api_url": api_url_full,
            "app_name": app_name,
            "stanza_name": stanza_name,
            "headers": {"Authorization": f"Bearer {token}"},
            "data": payload,
        })

    return api_calls

def process_metadata(file_path, api_url, token, app_name, api_caller):
    """
    Main function to parse metadata and trigger API calls.
    """
    parsed_data = parse_meta_with_configparser(file_path)
    api_calls = prepare_api_calls(parsed_data, api_url, token, app_name)

    for call in api_calls:
        api_caller(
            call["api_url"],
            call["app_name"],
            call["stanza_name"],
            call["headers"],
            call["data"]
        )

# if __name__ == "__main__":
#     import sys
#     from api_caller import make_api_call  # Import your existing api_caller.py functions

#     if len(sys.argv) < 5:
#         print("Usage: python metadata_parser.py <meta_file_path> <api_url> <token> <app_name>")
#         sys.exit(1)

#     meta_file_path = sys.argv[1]
#     api_url = sys.argv[2]
#     token = sys.argv[3]
#     app_name = sys.argv[4]

#     process_metadata(meta_file_path, api_url, token, app_name, make_api_call)
