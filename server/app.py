from flask import Flask, jsonify
from fetch_data import fetchAndSaveCsv
# from train_model import trainModel
from raw_data_management import isRainy, getLatestDate, getStartDate, deleteOldRawData, getCurrentDate, insertLatestDate, avgRawData, fillMissingWeek, deleteRainyWeek, deleteOldAvgWeekData

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def fetch_route():
    currentDate = getCurrentDate()
    latestDate = getLatestDate()
    startDate = getStartDate(currentDate)

    if (not isRainy(currentDate)):
        print("not rainy week, start operating ....")
        deleteOldRawData(startDate, "ndvi")
        deleteOldRawData(startDate, "ndmi")
        
        numOfNewFile = fetchAndSaveCsv(latestDate, currentDate)  # Call your function

        avgRawData("ndvi")
        avgRawData("ndmi")

        fillMissingWeek("ndvi", startDate, currentDate)
        fillMissingWeek("ndmi", startDate, currentDate)

        deleteOldAvgWeekData(startDate,"ndvi")
        deleteOldAvgWeekData(startDate,"ndmi")

        # deleteRainyWeek()
        # message = trainModel('NDMI')
    else : 
        print("rainy week, skip operation.")

    # insertLatestDate(currentDate)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)