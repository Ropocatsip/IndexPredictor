# import os
# import pandas as pd
# import numpy as np
# import re
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import TimeDistributed, Conv2D, MaxPooling2D, Flatten, LSTM, Dense
# from tensorflow.keras.callbacks import EarlyStopping
# from matplotlib import pyplot

# def extract_year_week(filename):
#     match = re.search(r'(\d{4})-week(\d+)', filename)
#     return (int(match.group(1)), int(match.group(2))) if match else (None, None)

# def load_and_preprocess_data(folder_path):
#     data_frames = []
#     week_info = []
    
#     for file in sorted(os.listdir(folder_path)):
#         if file.endswith(".csv"):
#             year, week = extract_year_week(file)
#             if year is not None and week is not None:
#                 df = pd.read_csv(os.path.join(folder_path, file))
#                 df = df.iloc[:, 1:]  # Remove first column 
#                 df = df.astype(float)  # Ensure numerical format
#                 data_frames.append(df.values)
#                 week_info.append((year, week))
    
#     data_frames = np.array(data_frames)  # Convert list to numpy array
    
#     # Normalize data
#     scaler = MinMaxScaler()
#     data_frames = np.array([scaler.fit_transform(frame) for frame in data_frames])
    
#     return data_frames, week_info, scaler

# def prepare_sequences(data, weeks, time_steps=6):
#     X, y, week_labels = [], [], []
#     for i in range(len(data) - time_steps):
#         X.append(data[i:i + time_steps])
#         y.append(data[i + time_steps])
#         week_labels.append(weeks[i + time_steps])
#     return np.array(X), np.array(y), week_labels

# def build_cnn_lstm_model(input_shape, output_size):
#     model = Sequential([
#         TimeDistributed(Conv2D(64, (3, 3), activation='relu', padding='same'), input_shape=input_shape),
#         TimeDistributed(MaxPooling2D((2, 2))),
#         TimeDistributed(Flatten()),
#         LSTM(100, activation='relu', return_sequences=False),
#         Dense(output_size, activation='tanh')
#     ])
    
#     model.compile(optimizer='adam', loss='mse', metrics=['mae'])
#     return model

# def trainModel(index):
#     # Load and preprocess data
#     folder_path = f"data/{index}/rawdata"
#     data, weeks, scaler = load_and_preprocess_data(folder_path)
#     X, y, week_labels = prepare_sequences(data, weeks)

#     # Split data: Train (2019-week42 to 2022-week20), Validate (2022-week42 to 2023-week20)
#     X_train, y_train, X_val, y_val = [], [], [], []
#     for i, (year, week) in enumerate(week_labels):
#         if (2019 <= year <= 2021) or (year == 2022 and week <= 20):
#             X_train.append(X[i])
#             y_train.append(y[i])
#         elif (year == 2022 and week >= 42) or (year == 2023 and week <= 20):
#             X_val.append(X[i])
#             y_val.append(y[i])

#     X_train, y_train = np.array(X_train), np.array(y_train)
#     X_val, y_val = np.array(X_val), np.array(y_val)

#     input_shape = (X.shape[1], X.shape[2], X.shape[3], 1)
#     output_size = y.shape[1] * y.shape[2]  # Ensure correct output size calculation
#     model = build_cnn_lstm_model(input_shape, output_size)

#     # Train the model
#     callbacks = [EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)]
#     history = model.fit(X_train, y_train.reshape(y_train.shape[0], -1), epochs=10, batch_size=16, validation_data=(X_val, y_val.reshape(y_val.shape[0], -1)), callbacks=callbacks)

#     # Save the model for transfer learning
#     # model.save("cnn_lstm_model-1.h5")

#     print(f"Processed data shape: {data.shape}")  # (num_weeks, height, width)
#     print(f"Train shape: {X_train.shape}, Validation shape: {X_val.shape}")  # Explicit split based on week numbers
#     model.save(f"models/{index}/cnn_lstm_{index}_model-n6.h5")