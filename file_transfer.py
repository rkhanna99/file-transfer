import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def copy_files(source_folder, destination_folder, max_workers=4, file_type=None, start_date=None, end_date=None):
    """
    Copies files from source_folder to destination_folder with optional filters.

    Parameters:
        source_folder (str): Path to the source directory.
        destination_folder (str): Path to the destination directory.
        max_workers (int): Number of threads for concurrent copying.
        file_type (str): File extension filter (e.g., ".txt").
        start_date (datetime): Filter for files modified after or on this date.
        end_date (datetime): Filter for files modified before or on this date.
    """
    os.makedirs(destination_folder, exist_ok=True)

    # Filter files based on criteria
    transfer_files = [
        f for f in os.listdir(source_folder)
        if (file_type is None or f.lower().endswith(file_type)) and
        (start_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) >= start_date) and
        (end_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) <= end_date)
    ]

    # Multithreaded file copying
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(shutil.copy2, os.path.join(source_folder, file_name), os.path.join(destination_folder, file_name))
            for file_name in transfer_files
        ]
        for future in as_completed(futures):
            future.result()
    
    return len(transfer_files)
