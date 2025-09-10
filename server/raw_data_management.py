from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
import re
from dotenv import load_dotenv

# Create a new client and connect to the server
try:
    load_dotenv()
    client = MongoClient(os.getenv("uri"), server_api=ServerApi('1'))
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    mydb = client["IndexPredictor"]
    mycol = mydb["indexRawData"]
except Exception as e:
    print(e)

def isRainy(currentDate):
    currentWeek = currentDate.isocalendar().week
    if (currentWeek > 20 and currentWeek < 45) : return True
    else: return False

def getLatestDate():
    latestDate = mycol.find_one(sort=[("_id", -1)])["LatestDate"]
    # latestWeek = latestDate.isocalendar().week
    print(f"Latest Date : {latestDate}")
    return latestDate

def getCurrentDate():
    # currentDate = datetime.now()
    currentDate = datetime(2025, 5, 18)
    print(f"Current Date : {currentDate}")
    return currentDate

def getStartDate(currentDate) : 
    startDate = currentDate - relativedelta(years=5)
    # startWeek = startDate.isocalendar().week
    print(f"Start Date : {startDate}")
    return startDate

def getPredictedDate(currentDate):

    # get ISO year & week
    iso_week = currentDate.isocalendar().week
    iso_year = currentDate.isocalendar().year
    
    # push one week
    if iso_week > 52:   # rollover
        iso_year += 1
        iso_week = 1
    elif iso_week == 20:  
        iso_week = 45
    else: 
        iso_week += 1

    return f"{iso_year}-week{iso_week}"

def insertLatestDate(currentDate):
    data = {
        "LatestDate": currentDate
    }
    mycol.insert_one(data)
    print("Inserted latest date success.")

def deleteOldRawData(startDate, indexType):

    # storage or raw data location file
    folder_path = f"data/{indexType}/rawdata"

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            try:
                date_str = filename.split("_")[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Compare dates
                if file_date < startDate:
                    file_path = os.path.join(folder_path, filename)
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
            except ValueError:
                print(f"Skipped (invalid date format): {filename}")

def deleteOldAvgWeekData(startDate, indexType):

    # storage or raw data location file
    folder_path = f"data/{indexType}/weekdata"

    def week_to_date(year, week):
        return datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
    
    pattern = re.compile(r"(\d{4})-week(\d{1,2})\.csv$")
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            year = int(match.group(1))
            week = int(match.group(2))
            file_date = week_to_date(year, week)
            if file_date < startDate:
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                print(f"Deleted: {filename}")

def avgRawData(indexType):
    # Folder containing CSV files
    input_folder = f"data/{indexType}/rawdata/"
    output_folder = f"data/{indexType}/weekdata/"

    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Function to extract date and week number from filename
    def get_week_info(filename):
        date_str = filename.split("_")[0]  # Extract date part
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        iso_year, week_number, _ = date_obj.isocalendar()  # ISO year, ISO week, weekday
        return iso_year, week_number

    # Read and group CSV files by (year, week)
    week_groups = {}
    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            year, week = get_week_info(file)
            output_file = os.path.join(output_folder, f"{year}-week{week:02}.csv")

            # skip if already have data
            if os.path.exists(output_file):
                # print(f"Skipped (already exists): {output_file}")
                continue

            filepath = os.path.join(input_folder, file)
            df = pd.read_csv(filepath, index_col=0)  # Skip first column as index
            if (year, week) not in week_groups:
                week_groups[(year, week)] = []
            week_groups[(year, week)].append(df)

    # Compute weekly average and save to CSV
    for (year, week), dfs in week_groups.items():
        if 21 <= week <= 44:
            continue
        output_file = os.path.join(output_folder, f"{year}-week{week:02}.csv")

        if os.path.exists(output_file):
            continue

        avg_df = sum(dfs) / len(dfs)  # Compute mean across all files in the same week
        avg_df.to_csv(output_file, index=True)
        print(f"Saved: {output_file}")

    print("Weekly average CSV files saved in:", output_folder)

def get_year_week(filename):
    """Extracts year and week number from filename (e.g., '2024-week4.csv' -> (2024, 4))."""
    parts = filename.split('-week')
    year = int(parts[0])
    week = int(parts[1].split('.csv')[0])
    return year, week

def linear_interpolation(existing_weeks, year, target_week, data_dict):
    """Interpolates values for the target week based on existing weeks and data, considering cross-year interpolation."""
    lower_week = max([w for w in existing_weeks if w < target_week], default=None)
    upper_week = min([w for w in existing_weeks if w > target_week], default=None)
    
    if lower_week is None:
        prev_year = year - 1
        if prev_year in data_dict and data_dict[prev_year]:
            last_prev_week = max(data_dict[prev_year].keys())
            return (data_dict[prev_year][last_prev_week] + data_dict[year][upper_week]) / 2
        return data_dict[year][upper_week]
    
    if upper_week is None:
        sorted_weeks = sorted(existing_weeks)
        if len(sorted_weeks) >= 2:
            w1, w2 = sorted_weeks[-2], sorted_weeks[-1]
            v1, v2 = data_dict[year][w1], data_dict[year][w2]
            slope = (v2 - v1) / (w2 - w1)
            extrapolated_data = v2 + slope * (target_week - w2)
            return extrapolated_data
        return data_dict[year][lower_week]
    
    lower_data = data_dict[year][lower_week]
    upper_data = data_dict[year][upper_week]
    weight = (target_week - lower_week) / (upper_week - lower_week)
    interpolated_data = lower_data + weight * (upper_data - lower_data)
    return interpolated_data

def fillMissingWeek(indexType, startDate, currentDate):
    folder = f"data/{indexType}/weekdata/"
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    
    # Read existing files into a dictionary
    data_dict = {}
    existing_weeks = {}

    def weeks_in_year(year: int) -> int:
        # ISO calendar: the last Thursday of the year decides the week count
        return date(year, 12, 28).isocalendar()[1]
    
    for file in files:
        year, week_number = get_year_week(file)
        df = pd.read_csv(os.path.join(folder, file), index_col=0)
        
        if year not in data_dict:
            data_dict[year] = {}
            existing_weeks[year] = []
        
        data_dict[year][week_number] = df.values
        existing_weeks[year].append(week_number)
    
    # Process each year separately
    for year in sorted(data_dict.keys()):
        existing_weeks[year].sort()
        num_weeks = weeks_in_year(year)
        all_weeks = set(range(1, num_weeks + 1))  # Ensure full year coverage
        missing_weeks = sorted(all_weeks - set(existing_weeks[year]))
        
        for week in missing_weeks:
            if 21 <= week <= 44:
                continue
            # Get the Monday of the given ISO week
            week_start_date = datetime.strptime(f'{year}-W{week-1}-1', "%Y-W%W-%w").date()
            # Only generate if within startDate and currentDate
            if startDate.date() <= week_start_date <= currentDate.date():
                interpolated_values = linear_interpolation(existing_weeks[year], year, week, data_dict)
                interpolated_df = pd.DataFrame(interpolated_values, columns=df.columns, index=df.index)
                output_file = os.path.join(folder, f'{year}-week{week:02}.csv')
                interpolated_df.to_csv(output_file)
                print(f'Generated {output_file}')

def saveIndexFromCsv(indexType, predictedWeek):
    targetList = [(207, 270), (125, 92)]
    # Specify the full path to your CSV file
    folder_path = f"data/{indexType}/weekdata"
    collection = mydb[indexType]
    # Read the CSV into a DataFrame

    all_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".csv")])

    # Take the last 8 files
    last_8_files = all_files[-8:]
    for target in targetList:
        x_target = target[0]
        y_target = target[1]
        index_data_list = []

        for file_name in last_8_files:
            week_name = file_name.replace(".csv", "")  # e.g., "2025-week20"
            file_path = os.path.join(folder_path, file_name)
            
            # Load CSV, assuming single value or a specific cell
            df = pd.read_csv(file_path, index_col=0) 
            
            value = df.iloc[x_target-2, y_target]
            
            index_data_list.append({
                "week": week_name,
                "data": float(value)
            })

        file_path = f"model/{indexType}/{predictedWeek}-predicted.csv"
        week_name = predictedWeek
        df = pd.read_csv(file_path, index_col=0) 
            
        value = df.iloc[x_target-2, y_target]
        
        index_data_list.append({
            "week": week_name,
            "data": float(value)
        })
        # Update MongoDB
        collection.update_one(
            {"xAxis": x_target, "yAxis": y_target},
            {"$set": {"indexData": index_data_list, "updateDate": datetime.now()}}
        )
        print(f"MongoDB document x: {x_target}, y: {y_target} updated successfully.")
    
        # Display the first few rows
