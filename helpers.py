from datetime import datetime as dt
import json
from PIL import Image
from PIL.ExifTags import TAGS
import os, time, pathlib, platform, time, exiftool
from typing import List
from exiftool import ExifToolHelper

# Path to the exiftool executable
EXIFTOOL_PATH = os.path.join(os.path.dirname(__file__), 'bin', 'exiftool.exe')

# Helper method to sort all files by type in a directory (Pillow supported images, RAW files with a corresponding jpg, RAW files without a corresponding jpg, and others)
def collect_files_by_type(directory: str):
    pillow_supported_imgs = {}
    raws_with_jpg = []
    raws_without_jpg = []
    others = []

    # temporary mapping raw file bases to their full paths
    raw_candidates = {}

    # Start iterating through all of the the files in the directory
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                name = entry.name
                ext = name.split('.')[-1].lower()
                base_name = os.path.splitext(name)[0]

                # Check if the file is a Pillow supported image
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
                    pillow_supported_imgs[base_name] = entry.path
                elif ext in ['cr2', 'nef', 'arw', 'orf', 'rw2', 'raf']:
                    raw_candidates[base_name] = entry.path
                else:
                    others.append(entry.path)

    # Iterate through the raw candidates to see if they have a jpg file in the same directory
    for base_name, raw_path in raw_candidates.items():
        if base_name in pillow_supported_imgs:
            raws_with_jpg.append(raw_path)
        else:
            raws_without_jpg.append(raw_path)    

    return pillow_supported_imgs, raws_with_jpg, raws_without_jpg, others


# Helper method to get the date taken of Pillow supported files
def get_date_taken_pillow(pillow_supported_imgs):
    try:
        # Initialize a map to store the date taken values
        date_map = {}

        for file_name, file_path in pillow_supported_imgs.items():
            # Open the image file using Pillow
            with Image.open(file_path) as img:
                # Get the EXIF data
                exif_data = img._getexif()
                if exif_data is not None:
                    # Iterate through the EXIF data to find the DateTimeOriginal tag
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            # Convert the value to a datetime object and store it in the map
                            date_taken = dt.strptime(value, '%Y:%m:%d %H:%M:%S')
                            date_map[file_name] = date_taken.date()
                            break
    except Exception as e:
        print(f"Error retrieving date taken for {file_name}: {e}")
        return None

    return date_map

# Helper method to get the date taken of the RAW files
def get_date_taken_raw(raw_files) -> set[str]:
    # Set for all the datetimes
    dates = set()

    # Check if the RAW file list is empty
    if not raw_files:
        print("No RAW files found that don't have a corresponding jpg")
        return dates

    # Set the needed tags for the batch exiftool call
    tags = [
        'EXIF:DateTimeOriginal',
        'QuickTime:CreationDate',
        'EXIF:CreateDate',
        'XMP:CreateDate'
    ]

    params = [f'-{tag}' for tag in tags]

    # Use the Exiftool in Batch mode to get the creation date for all files
    try:
        with ExifToolHelper(executable=EXIFTOOL_PATH) as et:
            metadata = et.get_metadata(raw_files, params=params)

        for data in metadata:
            # Check if the file has EXIF data
            for tag in ['EXIF:DateTimeOriginal', 'QuickTime:CreationDate', 'EXIF:CreateDate', 'XMP:CreateDate']:
                if tag in data.keys():
                    date_taken = data[tag]
                    # Convert to datetime object and return the date part
                    if isinstance(date_taken, str):
                        date_taken = dt.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                        dates.add(date_taken.date())
                    elif isinstance(date_taken, dt):
                        dates.add(date_taken.date())
                    break

    except Exception as e:
        print(f"Error retrieving dates for the RAW files: {e}")
    
    return dates


"""Gets creation dates for all files in a directory."""
def get_creation_dates_for_directory(directory) -> set[str]:

    # Set for all the datetimes
    dates = set()
    is_windows = platform.system() == 'Windows'

    # Collect all the files in the directory by type
    pillow_supported_imgs, raws_with_jpg, raws_without_jpg, others = collect_files_by_type(directory)

    # Get the date taken for the Pillow supported images
    pillow_dates = get_date_taken_pillow(pillow_supported_imgs)
    if pillow_dates:
        dates.update(pillow_dates.values())

    # Get the date taken for the RAW files (no need to process raws with jpgs)
    if raws_without_jpg:
        raw_dates = get_date_taken_raw(raws_without_jpg)
        if raw_dates:
            dates.update(raw_dates)

    # Get the date taken for the other files (we will default to the file creation date)
    for file_path in others:
        try:
            # Get the file creation time
            if is_windows:
                creation_time = os.path.getctime(file_path)
            else:
                stat = os.stat(file_path)
                creation_time = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime

            # Convert to datetime object and return the date part
            date_taken = dt.fromtimestamp(creation_time).date()
            dates.add(date_taken)
        except Exception as e:
            print(f"Error retrieving date for {file_path}: {e}")
    
    return dates

if __name__ == "__main__":
    #directory_path = "C:/Users/rahul/OneDrive/Pictures/Switzerland 2024/JPGs"
    directory_path = "E:/DCIM/100_FUJI"
    dates = get_creation_dates_for_directory(directory_path)
    print(f"Dates: {dates}")

