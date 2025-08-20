import os
import re
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import TimeDistributed, Conv2D, MaxPooling2D, Flatten, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

def deleteOldModel():
    # Path to your folder
    indexTypes = ["ndvi", "ndmi"]
    for indexType in indexTypes:
        folder_path = f"models/{indexType}"

        # File to delete
        file_name = "cnn_lstm_n6.h5"

        # Full path
        file_path = os.path.join(folder_path, file_name)

        # Check if file exists before deleting
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_name} deleted successfully.")
        else:
            print(f"{file_name} does not exist in {folder_path}.")

def splitTrainAndValidateData(folder):
    # Regex to extract year and week from filenames
    pattern = re.compile(r"(\d{4})-week(\d{2})\.csv")

    def parse_year_week(filename):
        match = pattern.match(filename)
        if match:
            year, week = int(match.group(1)), int(match.group(2))
            # Convert year-week to a comparable datetime (Monday of that week)
            return datetime.fromisocalendar(year, week, 1)
        return None

    # Get all CSV files that match the yyyy-weekxx pattern
    files = [f for f in os.listdir(folder) if pattern.match(f)]

    # Sort by actual date
    files_sorted = sorted(files, key=parse_year_week)

    # Split into train and validate
    validate = files_sorted[-28:]   # last 28 files
    train = files_sorted[:-28]      # all except last 28
    return train, validate
    # print("Train files:", train)
    # print("Validate files:", validate)

def trainModel():

    def extract_year_week(filename):
        match = re.search(r'(\d{4})-week(\d+)', filename)
        return (int(match.group(1)), int(match.group(2))) if match else (None, None)

    def load_and_preprocess_data(folder_path):
        data_frames = []
        week_info = []
        
        for file in sorted(os.listdir(folder_path)):
            if file.endswith(".csv"):
                year, week = extract_year_week(file)
                if year is not None and week is not None:
                    df = pd.read_csv(os.path.join(folder_path, file))
                    df = df.iloc[:, 1:]  # Remove first column 
                    df = df.astype(float)  # Ensure numerical format
                    data_frames.append(df.values)
                    week_info.append((year, week, file))  # keep filename too
        
        data_frames = np.array(data_frames)
        
        # Normalize each frame
        scaler = MinMaxScaler()
        data_frames = np.array([scaler.fit_transform(frame) for frame in data_frames])
        
        return data_frames, week_info, scaler
    
    def prepare_sequences(data, weeks, time_steps=6):
        X, y, week_labels = [], [], []
        for i in range(len(data) - time_steps):
            X.append(data[i:i + time_steps])
            y.append(data[i + time_steps])
            week_labels.append(weeks[i + time_steps][2])
        return np.array(X), np.array(y), week_labels

    def build_cnn_lstm_model(input_shape, output_size):
        model = Sequential([
            TimeDistributed(Conv2D(64, (3, 3), activation='relu', padding='same'), input_shape=input_shape),
            TimeDistributed(MaxPooling2D((2, 2))),
            TimeDistributed(Flatten()),
            LSTM(100, activation='relu', return_sequences=False),
            Dense(output_size, activation='tanh')
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    # Load and preprocess data
    folder_path = f"data/ndvi/weekdata"
    data, weeks, scaler = load_and_preprocess_data(folder_path)
    X, y, week_labels = prepare_sequences(data, weeks)

    train_files, val_files = splitTrainAndValidateData(folder_path)
    # Split data: Train (2019-week42 to 2022-week20), Validate (2022-week42 to 2023-week20)
    X_train, y_train, X_val, y_val = [], [], [], []
    for i, file in enumerate(week_labels):
        if file in train_files:
            X_train.append(X[i])
            y_train.append(y[i])
        elif file in val_files:
            X_val.append(X[i])
            y_val.append(y[i])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_val, y_val = np.array(X_val), np.array(y_val)

    input_shape = (X.shape[1], X.shape[2], X.shape[3], 1)
    output_size = y.shape[1] * y.shape[2]  # Ensure correct output size calculation
    model = build_cnn_lstm_model(input_shape, output_size)

    # Train the model
    callbacks = [EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)]
    history = model.fit(X_train, y_train.reshape(y_train.shape[0], -1), epochs=10, batch_size=16, validation_data=(X_val, y_val.reshape(y_val.shape[0], -1)), callbacks=callbacks)

    print(f"Processed data shape: {data.shape}")  # (num_weeks, height, width)
    print(f"Train shape: {X_train.shape}, Validation shape: {X_val.shape}")  # Explicit split based on week numbers
    model.save("model/ndvi/cnn_lstm_n6.h5")
    print(f"Model saved successful.")
