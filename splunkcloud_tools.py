### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import sys
import os
import argparse

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from module_checker import check_modules

__name__ = "splunkcloud_tools.py"
__author__ = "Michel de Jong"

def splunkcloud_tools(args):
    try:
        # Select which script
        selection = input("Select which script you want to use: \n 1) Disable Savedsearches (pre-deployment) \n 2) Enable scheduled searches (post-deployment) \n 3) Create all Savedsearches \n")
        if selection == "1":
            if args.debug is False:
                debug = input("Enable debug logging? (create an extra logfile with debug logs) (y/n) \n")
                if debug.lower() == "y":
                    args.debug = True
            required_modules = ['shutil', 'datetime', 'datetime']
            check_modules(required_modules)
            from disabling_savedsearches import disabling_savedsearches
            disabling_savedsearches(args)
            print("Finished. Exiting the script")
            exit(0)
        if selection == "2" or selection =="3":
            if args.debug is False:
                debug = input("Enable debug logging? (create an extra logfile with debug logs) (y/n) \n")
                if debug.lower() == "y":
                    args.debug = True
                elif debug.lower() == "n":
                    args.debug = False
                else:
                    print("Invalid input. Exiting the script.")
            if args.dummy is False:
                dummy = input("Enable dummy mode? (bypasses the actual API calls) (y/n) \n")
                if dummy.lower() == "y":
                    args.dummy = True
                elif dummy.lower() == "n":
                    args.dummy = False
                else:
                    print("Invalid input. Exiting the script.")
            
            required_modules = ['re', 'getpass', 'urllib.parse', 'requests', 'datetime']
            check_modules(required_modules)

            from rest_update_savedsearches import rest_bulk_update_savedsearches
            if selection == "2":
                args.enable = True
                rest_bulk_update_savedsearches(args)
                print("Finished. Exiting the script.")
                exit(0)
            if selection == "3":
                args.create = True
                rest_bulk_update_savedsearches(args)
                print("Finished. Exiting the script.")
                exit(0)
        else:
            print("Exiting the script.")
            exit(0)

    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "splunkcloud_tools.py":
    parser = argparse.ArgumentParser(description="Splunk Cloud tools to disable scheduled searches in a given directory with apps (pre-deployment), enable scheduled searches on specific endpoints based on a given directory with apps (post-search-deployment) and create savedsearches (post-app-deployment). Please refer the README.md for more information.")
    parser.add_argument("-debug", action="store_true", help="Enable debug mode, create an extra logfile with all debug logs")
    parser.add_argument("-dummy", action="store_true", help="Run in dummy mode, bypasses the actual API calls when running the enable scheduled searches script")
    args = parser.parse_args()
    args.create = False
    args.enable = False

    splunkcloud_tools(args)