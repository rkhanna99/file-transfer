import os
import time
from collections import defaultdict
from datetime import datetime
from PIL import Image, ExifTags
import rawpy, piexif, platform, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Extended file extensions for RAW and image types
IMAGE_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.tiff', '.bmp',  # Standard image formats
    '.raf', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.srw', '.dng', '.rw2', '.pef', '.iiq', '.erf', '.3fr'  # RAW formats
)

def extract_file_date(file_path):
    """
    Extracts the date taken (for images) or the file creation date.
    """

    # Initialize date_taken as None before attempting to retrieve the date.
    date_taken = None

    try:
        # Handle image or RAW file date taken
        if file_path.lower().endswith(IMAGE_EXTENSIONS):
            date_taken = get_image_date_taken(file_path)
            if date_taken:
                return date_taken

        # Fallback to file system creation date
        try:
            if platform.system() == 'Windows':
                # For Windows
                ctime = os.path.getctime(file_path)
            else:
                # For Unix/Linux/MacOS
                stat = os.stat(file_path)
                # Use st_birthtime if available (only on MacOS, not Linux)
                ctime = getattr(stat, 'st_birthtime', stat.st_mtime)
            
            # Format the time as a string
            return datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
    
        except Exception as e:
            print(f"Error retrieving creation date for {file_path}: {e}")
            return None
    except Exception as e:
        print(f"Error retrieving date for {file_path}: {e}")
        return None

def get_creation_dates(folder_path):
    """
    Extracts creation dates or date taken (for images, including RAW files) from the source folder.
    Uses threading for faster processing.
    """
    creation_dates = defaultdict(list)
    try:
        # List all files in the folder
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=8) as executor:
            for file_path, date in zip(files, executor.map(extract_file_date, files)):
                if date:
                    creation_dates[date].append(os.path.basename(file_path))

    except Exception as e:
        print(f"Error processing folder {folder_path}: {e}")
    
    return creation_dates

def get_image_date_taken(image_path):
    """
    Extracts the 'Date Taken' metadata from an image file or RAW file.
    Returns the date in 'YYYY-MM-DD' format, or None if not available.
    """
    try:
        if image_path.lower().endswith(IMAGE_EXTENSIONS[-13:]):  # Check if the file is a RAW format
            return get_raw_image_date_taken(image_path)
        else:  # Handle standard image files
            with Image.open(image_path) as img:
                exif_data = img._getexif()  # Retrieve EXIF data
                if not exif_data:
                    return None
                
                # Map the EXIF tag to readable format
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
                
                # Extract the DateTimeOriginal tag (commonly used for date taken)
                date_taken = exif.get('DateTimeOriginal') or exif.get('DateTime')
                if date_taken:
                    # Format the date to 'YYYY-MM-DD'
                    date_taken = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d")
                    return date_taken
    except Exception as e:
        print(f"Error reading metadata for {image_path}: {e}")
    
    return None


def get_raw_image_date_taken(file_path):
    """
    Extracts the date taken from RAW image files using exiftool.
    """
    try:
        # Run the exiftool command to get DateTimeOriginal
        result = subprocess.run(
            ["exiftool", "-DateTimeOriginal", "-s", "-s", "-s", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result)
        # Check for errors
        if result.stderr:
            raise Exception(result.stderr.strip())

        # Parse the result (format: "YYYY:MM:DD HH:MM:SS")
        date_taken = result.stdout.strip()
        if date_taken:
            return date_taken.split(" ")[0].replace(":", "-")  # Format as YYYY-MM-DD
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")

    return None


if __name__ == "__main__":
    directory_path = "/Volumes/NO NAME/RAFs"
    dates = get_creation_dates(directory_path)
    print(f"Dates: {dates}")

