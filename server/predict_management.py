import os
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

input_folder = "data/ndvi/weekdata"
output_folder = "model/ndvi"
model_path = "model/ndvi/cnn_lstm_n6.h5"
sequence_length = 6  # how many weeks the model expects

os.makedirs(output_folder, exist_ok=True)

def extract_year_week(filename):
    match = re.search(r'(\d{4})-week(\d+)', filename)
    return (int(match.group(1)), int(match.group(2))) if match else (None, None)

def load_and_preprocess_data(folder_path):
    """Load and preprocess CSV files, return dict and scalers"""
    data_frames = {}
    scaler_dict = {}
    for file in sorted(os.listdir(folder_path)):
        if file.endswith(".csv"):
            year, week = extract_year_week(file)
            if year is not None and week is not None:
                df = pd.read_csv(os.path.join(folder_path, file))
                df = df.iloc[:, 1:]  # drop index col
                df = df.astype(float)

                scaler = MinMaxScaler()
                normalized_data = scaler.fit_transform(df.values)

                data_frames[(year, week)] = normalized_data
                scaler_dict[(year, week)] = scaler
    return data_frames, scaler_dict

def prepare_input_sequence(data_dict, input_weeks):
    """Stack weeks into numpy array"""
    input_data = [data_dict[w] for w in input_weeks if w in data_dict]
    return np.array(input_data) if len(input_data) == sequence_length else None

def predictModel():
    # === LOAD MODEL ===
    model = load_model(model_path, compile=False)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # === LOAD DATA ===
    data_dict, scaler_dict = load_and_preprocess_data(input_folder)
    weeks_sorted = sorted(data_dict.keys())

    # === TAKE LAST SEQUENCE ===
    last_weeks = weeks_sorted[-sequence_length:]       # last 6 weeks
    next_week = (last_weeks[-1][0], last_weeks[-1][1] + 1)  # predict week+1 (naive)

    input_data = prepare_input_sequence(data_dict, last_weeks)

    if input_data is not None:
        # Shape for model
        input_data = np.expand_dims(input_data, axis=-1)  # add channel
        input_data = np.expand_dims(input_data, axis=0)   # add batch

        # Predict
        predicted_output = model.predict(input_data)
        predicted_output = predicted_output.reshape(data_dict[last_weeks[-1]].shape)

        # Use last scaler for inverse transform
        scaler = scaler_dict[last_weeks[-1]]
        predicted_output = scaler.inverse_transform(predicted_output)

        # Save to CSV
        output_filename = f"{next_week[0]}-week{next_week[1]}-predicted.csv"
        output_path = os.path.join(output_folder, output_filename)
        pd.DataFrame(predicted_output).to_csv(output_path, index=False)

        print(f"Saved prediction for next week: {output_filename}")
    else:
        print("Not enough data to prepare input sequence.")

