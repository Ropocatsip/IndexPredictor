from flask import Flask, jsonify, send_file
from flask_apscheduler import APScheduler
from fetch_data import fetchAndSaveCsv, fetchAndSaveRasterCsv
from raw_data_management import isRainy, getLatestDate, getStartDate, deleteOldRawData, getCurrentDate, insertLatestDate, avgRawData, fillMissingWeek, deleteOldAvgWeekData, saveIndexFromCsv, getPredictedDate
from model_management import trainModel
from predict_management import predictModel, convertToPng, mergeBetweenIndexAndRaster, applyZeroMaskFromOriginal
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@app.route('/predict', methods=['POST'])
def fetch_route():
    currentDate = getCurrentDate()
    latestDate = getLatestDate()
    startDate = getStartDate(currentDate)
    predictedWeek = getPredictedDate(currentDate)

    if (not isRainy(currentDate)):
        print("not rainy week, start operating ....")
        # ---- data preparation ----
        deleteOldRawData(startDate, "ndvi")
        deleteOldRawData(startDate, "ndmi")

        fetchAndSaveCsv(latestDate, currentDate)
        fetchAndSaveRasterCsv(latestDate, currentDate)
        avgRawData("ndvi")
        avgRawData("ndmi")

        fillMissingWeek("ndvi", startDate, currentDate)
        fillMissingWeek("ndmi", startDate, currentDate)

        deleteOldAvgWeekData(startDate,"ndvi")
        deleteOldAvgWeekData(startDate,"ndmi")

        # # ---- train model ----
        trainModel("ndvi")
        trainModel("ndmi")
        predictModel("ndvi")
        predictModel("ndmi")
        applyZeroMaskFromOriginal("ndvi", predictedWeek)
        applyZeroMaskFromOriginal("ndmi", predictedWeek)
        # ---- web presentation ----
        convertToPng("ndvi", predictedWeek)
        convertToPng("ndmi", predictedWeek)
        mergeBetweenIndexAndRaster(predictedWeek, "ndvi")
        mergeBetweenIndexAndRaster(predictedWeek, "ndmi")
        saveIndexFromCsv("ndvi", predictedWeek, None, None)
        saveIndexFromCsv("ndmi", predictedWeek, None, None)
        
    else : 
        print("rainy week, skip operation.")

    insertLatestDate(currentDate)
    return jsonify({'status': 'success'})

@app.route('/predict/png/<indexType>/<predictedWeek>', methods=['GET'])
def predict_picture(indexType, predictedWeek):
    return send_file(f"model/{indexType}/{predictedWeek}-merged.png", mimetype="image/png")

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

@app.route('/coordinates/<indexType>/<xAxis>/<yAxis>', methods=['POST'])
def save_index_from_csv(indexType, xAxis, yAxis):
    currentDate = getCurrentDate()
    predictedWeek = getPredictedDate(currentDate)
    saveIndexFromCsv(indexType, predictedWeek, xAxis, yAxis)
    return jsonify({"success": True}), 200

scheduler.add_job(id='weekly_job', func=fetch_route, trigger='cron', day_of_week='sun', hour=23, minute=0)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)