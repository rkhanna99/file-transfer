import os
import shutil
from datetime import datetime as dt
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

def copy_files(date_file_map: dict[dt.date, List[str]], source_folder, destination_folder, max_workers=4, file_type=None, start_date=None, end_date=None):
    """
    Copies files from source_folder to destination_folder with optional filters.

    Parameters:
        date_file_map (dict[dt.date, List[str]]): Map of dates to file paths.
        source_folder (str): Path to the source directory.
        destination_folder (str): Path to the destination directory.
        max_workers (int): Number of threads for concurrent copying.
        file_type (str): File extension filter (e.g., ".txt").
        start_date (datetime): Filter for files modified after or on this date.
        end_date (datetime): Filter for files modified before or on this date.
    """
    os.makedirs(destination_folder, exist_ok=True)

    transfer_files = []

    # Get a set of the dates that are in the date_file_map
    date_set = set(date_file_map.keys())

    # Iterate through the set of dates to identify which files to copy
    for date in date_set:
        if date >= start_date.date() and date <= end_date.date():
            # Get the list of files for this date
            files = date_file_map[date]
            for file in files:
                # Check if the file type matches and the file is not already in the transfer list
                if file_type is None or file.lower().endswith(file_type) and file not in transfer_files:
                    transfer_files.append(file)
                    print(f"Adding {file} to the transfer list")

    # Filter files based on the file type and date range (Using the date_file_map)
    # transfer_files_old_method = [
    #     f for f in os.listdir(source_folder)
    #     if (file_type is None or f.lower().endswith(file_type)) and
    #     (start_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) >= start_date) and
    #     (end_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) <= end_date)
    # ]

    # Multithreaded file copying
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(copy_file, file_name, source_folder, destination_folder)
            for file_name in transfer_files
        ]
        for future in as_completed(futures):
            future.result()
    
    return len(transfer_files)


# Helper function to copy a single file
def copy_file(file_name, source_folder, destination_folder):
    """
    Copies a single file from source_folder to destination_folder.

    Parameters:
        file_name (str): Name of the file to copy.
        source_folder (str): Path to the source directory.
        destination_folder (str): Path to the destination directory.
    """
    # Get the basename of the file
    file_name = os.path.basename(file_name)

    # Set the destination path
    destination_path = os.path.join(destination_folder, file_name)

    # Check if the file already exists in the destination folder
    if os.path.exists(destination_path):
        print(f"File {file_name} already exists in {destination_folder}. Skipping copy.")
        return
    
    # Copy the file
    try:
        shutil.copy2(os.path.join(source_folder, file_name), destination_path)
        print(f"Copied {file_name} to {destination_folder}")
    except FileNotFoundError:
        print(f"File {file_name} not found in {source_folder}. Skipping copy.")
        return
    except PermissionError:
        print(f"Permission denied for {file_name}. Skipping copy.")
        return

    