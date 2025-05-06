import os, shutil, argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Coding up a solution to copy files of a certain type from one directory to another using the command line
# If not provided a file type just move everything
def copy_files(source_folder: str, destination_folder: str, max_workers: int=4, file_type: str=None, start_date: datetime=None, end_date: datetime=None) -> None:

    # Check to see if the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Files to transfer and check if they already exist in the destination folder
    transfer_files = [
        f for f in os.listdir(source_folder)
        if (file_type is None or f.lower().endswith(file_type)) and
        (start_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) >= start_date) and
        (end_date is None or datetime.fromtimestamp(os.path.getmtime(os.path.join(source_folder, f))) <= end_date) and
        not os.path.exists(os.path.join(destination_folder, f))
    ]

    print(f"Files to transfer: {transfer_files}")

    # Utilize Multithreading
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(copy_file, os.path.join(source_folder, file_name), os.path.join(destination_folder, file_name), file_name)
            for file_name in transfer_files
        ]

        for future in as_completed(futures):
            future.result()

    

# Helper function that will copy a file from one destination to another
def copy_file(source_path, destination_path, file_name):
    shutil.copy2(source_path, destination_path)
    print(f"Copied {file_name} to {destination_path}")


# Main method
if __name__ == "__main__":
    # Setting up the command line args
    parser = argparse.ArgumentParser(description="Copy files from one directory to another optionally given a file type")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("destination_folder", help="Path to the destination folder")
    parser.add_argument("--workers", type=int, default=4, help="Number of threads used in the copying process")
    parser.add_argument("--file_type", help="Specify what files you want to copy")
    parser.add_argument("--start_date", help="Date to specify which files to copy (After or on that day)")
    parser.add_argument("--end_date", help="Date to specify which files to copy(Before or on that day)")
    args = parser.parse_args()

    # Parse the date if needed
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    print(start_date)
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
    print(end_date)

    # Run the function given the command line args
    copy_files(args.source_folder, args.destination_folder, max_workers=args.workers, file_type=args.file_type, start_date=start_date, end_date=end_date)
    print("Finished transferring all files")