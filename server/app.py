from flask import Flask, jsonify
from fetch_data import fetchAndSaveCsv
# from train_model import trainModel
from date_management import isRainy
from raw_data_management import getLatestDate, getStartDate, deleteOldRawData, getCurrentDate, insertLatestDate

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def fetch_route():
    if (not isRainy()):
        print("not rainy week")
        currentDate = getCurrentDate()
        latestDate = getLatestDate()
        startDate = getStartDate()
        deleteOldRawData(startDate)

        message = fetchAndSaveCsv(latestDate, currentDate)  # Call your function
        # message = trainModel('NDMI')
    else : 
        print("rainy week")

    # insertLatestDate(currentDate)
    return jsonify({'status': 'success', 'message': message})

if __name__ == '__main__':
    app.run(debug=True)