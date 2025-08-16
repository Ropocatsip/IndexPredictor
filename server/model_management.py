import os
import re
from datetime import datetime

def deleteOldModel():
    # Path to your folder
    indexTypes = ["ndvi", "ndmi"]
    for indexType in indexTypes:
        folder_path = f"models/{indexType}"

        # File to delete
        file_name = "my_model.h5"

        # Full path
        file_path = os.path.join(folder_path, file_name)

        # Check if file exists before deleting
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_name} deleted successfully.")
        else:
            print(f"{file_name} does not exist in {folder_path}.")

def splitTrainAndValidateData():
    folder = "data/ndvi/weekdata"
    # Regex to extract year and week from filenames
    pattern = re.compile(r"(\d{4})-week(\d{2})\.csv")

    def parse_year_week(filename):
        match = pattern.match(filename)
        if match:
            year, week = int(match.group(1)), int(match.group(2))
            # Convert year-week to a comparable datetime (Monday of that week)
            return datetime.fromisocalendar(year, week, 1)
        return None

    # Get all CSV files that match the yyyy-weekxx pattern
    files = [f for f in os.listdir(folder) if pattern.match(f)]

    # Sort by actual date
    files_sorted = sorted(files, key=parse_year_week)

    # Split into train and validate
    validate = files_sorted[-28:]   # last 28 files
    train = files_sorted[:-28]      # all except last 28

    # print("Train files:", train)
    # print("Validate files:", validate)