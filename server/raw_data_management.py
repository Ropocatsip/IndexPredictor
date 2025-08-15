from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

uri = "mongodb+srv://6672030421:1234@production.rzzjqkc.mongodb.net/?retryWrites=true&w=majority&appName=Production"
# Create a new client and connect to the server
try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    mydb = client["IndexPredictor"]
    mycol = mydb["indexRawData"]
except Exception as e:
    print(e)


def getLatestDate():
    latestDate = mycol.find_one(sort=[("_id", -1)])["LatestDate"]
    # latestWeek = latestDate.isocalendar().week
    print(f"Latest Week : {latestDate}")
    return latestDate

def getStartDate() : 
    startDate = datetime.now() - relativedelta(years=5)
    # startWeek = startDate.isocalendar().week
    print(f"Start Date : {startDate}")
    return startDate

def deleteOldRawData(startDate):

    # storage or raw data location file
    folder_path = "data/ndvi/rawdata"

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            try:
                # Extract date part from filename (before "_ndvi.csv")
                date_str = filename.split("_")[0]  # e.g., "2020-08-01"
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Compare dates
                if file_date < startDate:
                    file_path = os.path.join(folder_path, filename)
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
            except ValueError:
                print(f"Skipped (invalid date format): {filename}")
    return True