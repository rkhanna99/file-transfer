import os, shutil, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Coding up a solution to copy files of a certain type from one directory to another using the command line
# If not provided a file type just move everything
def copy_files(source_folder: str, destination_folder: str, max_workers: int=4, file_type: str=None) -> None:
    
    # Check to see if the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Files to transfer
    if file_type != None:
        transfer_files = [f for f in os.listdir(source_folder) if f.lower().endswith(file_type)]
    else:
        transfer_files = [f for f in os.listdir(source_folder)]

    # Utilize Multithreading
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(copy_file, os.path.join(source_folder, file_name), os.path.join(destination_folder, file_name), file_name)
            for file_name in transfer_files
        ]

        for future in as_completed(futures):
            future.result()

    # if file_type != None:
    #     for file_name in os.listdir(source_folder):
    #         if file_name.lower().endswith(file_type):
    #             # Set the source and destination paths
    #             source_path = os.path.join(source_folder, file_name)
    #             destination_path = os.path.join(destination_folder, file_name)
    #             # Copy the files
    #             shutil.copy2(source_path, destination_path)
    #             print(f"Copied {file_name} to {destination_folder}")
    #     print(f"Transfered all files of type '{file_type}'")
    # else:
    #     for file_name in os.listdir(source_folder):
    #         source_path = os.path.join(source_folder, file_name)
    #         destination_path = os.path.join(destination_folder, file_name)
    #         # Copy the files
    #         shutil.copy2(source_path, destination_path)
    #         print(f"Copied {file_name} to {destination_folder}")
    #     print("Transferred all files")

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
    parser.add_argument("file_type", help="Specify what files you want to copy")
    args = parser.parse_args()

    # Run the function given the command line args
    copy_files(args.source_folder, args.destination_folder, args.workers, args.file_type)
    print("Finished transferring all files")

    