### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import importlib
import subprocess

def check_modules(modules):
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError:
            print(f"{module} is not installed.")
            decision = input(f"Do you want to install {module}? (y/n): \n")
            if decision.lower() == "y":
                print(f"Installing...")
                try:
                    subprocess.check_call(['pip3', 'install', module])
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    print("Exiting the script")
                    exit(0)
            else:
                print("Exiting the script")
                exit(0)
            print(f"{module} has been successfully installed.")