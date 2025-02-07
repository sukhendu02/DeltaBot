# utils/logging_util.py

import datetime

def log_message(message):
    """
    Logs messages to the console and a log file.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    # Save log to a file
    try:
        with open("logfile.txt", "a", encoding="utf-8") as file:
            file.write(log_entry + "\n")
    except UnicodeEncodeError as e:
        print(f"Error: {e}")