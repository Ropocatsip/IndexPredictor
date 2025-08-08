from flask import Flask, jsonify
from fetch_data import fetchAndSaveCsv

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def fetch_route():
    message = fetchAndSaveCsv()  # Call your function
    return jsonify({'status': 'success', 'message': message})

if __name__ == '__main__':
    app.run(debug=True)