import os, time, pathlib, platform, time
from typing import List

def get_creation_date(path_to_file):
    """Gets the creation date of a file, falling back to the last modification date if necessary."""
    try:
        if platform.system() == 'Windows':
            # For Windows
            ctime = os.path.getctime(path_to_file)
        else:
            # For Unix/Linux/MacOS
            stat = os.stat(path_to_file)
            # Use st_birthtime if available (only on macOS, not Linux)
            ctime = getattr(stat, 'st_birthtime', stat.st_mtime)
        
        # Format the time as a string
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ctime))
    
    except Exception as e:
        print(f"Error retrieving creation date for {path_to_file}: {e}")
        return None

def get_creation_dates_for_directory(directory) -> List[str]:
    """Gets creation dates for all files in a directory."""

    # List for all the datetimes
    dates = []

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            curr = get_creation_date(filepath)
            dates.append(curr)
            print(f"{filename}: {get_creation_date(filepath)}")
    
    return dates

if __name__ == "__main__":
    directory_path = "/Users/rkhanna/Downloads"
    dates = get_creation_dates_for_directory(directory_path)
    print(f"Dates: {dates}")

