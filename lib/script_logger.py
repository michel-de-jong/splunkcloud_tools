import os
import datetime

def log_message(name, message, level):
    log_directory = create_log_directory(name)
    log_file = os.path.join(log_directory, f"{level}.log")

    with open(log_file, "a") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] [{level.upper()}] {message}\n")

def create_log_directory(name):
    try:     
        date = datetime.datetime.now().strftime("%Y%m%d")
        name = name.replace(".py", "")
        directory_name = os.path.join("logs", f"{name}_{date}")
        
        # Attempt to create the directory, handling any potential errors
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        
        return directory_name

    except OSError as e:
        # Handle directory creation errors
        print(f"Error creating directory: {e}")
        return None
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None
