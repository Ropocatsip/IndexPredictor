from flask import Flask, jsonify, send_file
from fetch_data import fetchAndSaveCsv
from raw_data_management import isRainy, getLatestDate, getStartDate, deleteOldRawData, getCurrentDate, insertLatestDate, avgRawData, fillMissingWeek, deleteOldAvgWeekData
from model_management import deleteOldModel, trainModel
from predict_management import predictModel, convertToPng
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def fetch_route():
    currentDate = getCurrentDate()
    latestDate = getLatestDate()
    startDate = getStartDate(currentDate)

    if (not isRainy(currentDate)):
        print("not rainy week, start operating ....")
        # data preparation
        deleteOldRawData(startDate, "ndvi")
        deleteOldRawData(startDate, "ndmi")

        fetchAndSaveCsv(latestDate, currentDate)

        avgRawData("ndvi")
        avgRawData("ndmi")

        fillMissingWeek("ndvi", startDate, currentDate)
        fillMissingWeek("ndmi", startDate, currentDate)

        deleteOldAvgWeekData(startDate,"ndvi")
        deleteOldAvgWeekData(startDate,"ndmi")

        # train model
        # deleteOldModel()
        # trainModel("ndvi")
        # trainModel("ndmi")
        predictModel("ndvi")
        predictModel("ndmi")
        convertToPng("ndvi")
        convertToPng("ndmi")
        # message = trainModel('NDMI')
    else : 
        print("rainy week, skip operation.")

    # insertLatestDate(currentDate)
    return jsonify({'status': 'success'})

@app.route('/predict/png/<indexType>/<predictedWeek>', methods=['GET'])
def predict_picture(indexType, predictedWeek):
    return send_file(f"model/{indexType}/{predictedWeek}-predicted.png", mimetype="image/png")

@app.route('/predict/csv/<indexType>/<predictedWeek>', methods=['GET'])
def predict_csv(indexType, predictedWeek):
    # Path to your CSV file
    file_path = f"model/{indexType}/{predictedWeek}-predicted.csv"
    
    # Send CSV file as a download
    return send_file(
        file_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"{predictedWeek}-predicted.csv"
    )

if __name__ == '__main__':
    app.run(debug=True)