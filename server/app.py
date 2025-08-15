from flask import Flask, jsonify
from fetch_data import fetchAndSaveCsv
# from train_model import trainModel
from date_management import isRainy
from raw_data_management import getLatestDate, getStartDate, deleteOldRawData

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def fetch_route():
    if (not isRainy()):
        print("not rainy week")
        latestDate = getLatestDate()
        startDate = getStartDate()
        deleteOldRawData(startDate)
        # message = fetchAndSaveCsv()  # Call your function
        # message = trainModel('NDMI')
    else : print("rainy week")
    return jsonify({'status': 'success', 'message': startDate})

if __name__ == '__main__':
    app.run(debug=True)