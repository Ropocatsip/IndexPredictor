from flask import Flask, jsonify
from fetch_data import fetchAndSaveCsv
# from train_model import trainModel
from raw_data_management import isRainy, getLatestDate, getStartDate, deleteOldRawData, getCurrentDate, insertLatestDate, avgRawData

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def fetch_route():
    if (not isRainy()):
        print("not rainy week")
        currentDate = getCurrentDate()
        latestDate = getLatestDate()
        startDate = getStartDate()
        deleteOldRawData(startDate)
        numOfNewFile = fetchAndSaveCsv(latestDate, currentDate)  # Call your function
        avgRawData("ndvi")
        avgRawData("ndmi")
        # message = trainModel('NDMI')
    else : 
        print("rainy week")

    # insertLatestDate(currentDate)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)