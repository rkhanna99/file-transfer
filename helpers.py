from collections import defaultdict
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


# Helper method to get the date taken of Pillow supported files (Will return a map of dates to the file paths)
def get_date_taken_pillow(pillow_supported_imgs: dict) -> dict[dt.date, List[str]]:
    try:
        # Initialize a map to store the date taken values
        date_map = defaultdict(list)

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
                            date_taken = dt.strptime(value, '%Y:%m:%d %H:%M:%S').date()
                            date_map[date_taken].append(file_path)
                            break
    except Exception as e:
        print(f"Error retrieving date taken for {file_name}: {e}")
        return None

    return date_map

# Helper method to get the date taken of the RAW files
def get_date_taken_raw(raw_files) -> dict[dt.date, List[str]]:
    # Set for all the datetimes
    date_map = defaultdict(list)

    # Check if the RAW file list is empty
    if not raw_files:
        print("No RAW files found that don't have a corresponding jpg")
        return date_map

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
                    # Convert to datetime object and update the date_map
                    if isinstance(date_taken, str):
                        date_taken = dt.strptime(date_taken, '%Y:%m:%d %H:%M:%S').date()
                        date_map[date_taken].append(data['SourceFile'])
                    elif isinstance(date_taken, dt):
                        dates_taken = date_taken.date()
                        date_map[dates_taken].append(data['SourceFile'])
                    break

    except Exception as e:
        print(f"Error retrieving dates for the RAW files: {e}")
    
    return date_map


# Helper method to get the creation dates for all files in a directory (Will return a set of dates and a map of dates to the file paths)
def get_creation_dates_for_directory(directory) -> dict[dt.date, List[str]]:

    # Return a map of dates to the file paths
    date_map = defaultdict(list)
    

    # Collect all the files in the directory by type
    pillow_supported_imgs, raws_with_jpg, raws_without_jpg, others = collect_files_by_type(directory)

    # Get the date taken for the Pillow supported images
    pillow_date_map = get_date_taken_pillow(pillow_supported_imgs)
    if pillow_date_map:
        for date_taken, file_paths in pillow_date_map.items():
            if date_map.get(date_taken) is None:
                date_map[date_taken] = file_paths
            else:
                date_map[date_taken].extend(file_paths)

    # Get the date taken for the RAW files (no need to process raws with jpgs)
    if raws_without_jpg:
        raw_date_map = get_date_taken_raw(raws_without_jpg)
        if raw_date_map:
            for date_taken, file_paths in raw_date_map.items():
                if date_map.get(date_taken) is None:
                    date_map[date_taken] = file_paths
                else:
                    date_map[date_taken].extend(file_paths)

    # Get the date taken for the other files (we will default to the file creation date)
    is_windows = platform.system() == 'Windows'
    for file_path in others:
        try:
            # Get the file creation time
            if is_windows:
                creation_time = os.path.getctime(file_path)
            else:
                stat = os.stat(file_path)
                creation_time = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime

            # Convert to datetime object and update the date map
            date_taken = dt.fromtimestamp(creation_time).date()
            if date_map.get(date_taken) is None:
                date_map[date_taken] = [file_path]
            else:
                date_map[date_taken].append(file_path)

        except Exception as e:
            print(f"Error retrieving date for {file_path}: {e}")
    
    return date_map

# Test the helper methods here if needed
if __name__ == "__main__":
    #directory_path = "C:/Users/rahul/OneDrive/Pictures/Switzerland 2024/JPGs"
    directory_path = "E:/DCIM/100_FUJI"
    date_map = get_creation_dates_for_directory(directory_path)

    # Return a set of dates from the date_map
    dates = set(date_map.keys())
    print(f"Dates: {dates}")
    print(f"Unique Dates: {len(dates)}")

