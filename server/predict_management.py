import os
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import matplotlib.cm as cm
from PIL import Image, ImageDraw

sequence_length = 6 

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

def predictModel(indexType):
    input_folder = f"data/{indexType}/weekdata"
    output_folder = f"model/{indexType}"
    model_path = f"model/{indexType}/cnn_lstm_n6.h5"

    os.makedirs(output_folder, exist_ok=True)
    # === LOAD MODEL ===
    model = load_model(model_path, compile=False)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # === LOAD DATA ===
    data_dict, scaler_dict = load_and_preprocess_data(input_folder)
    weeks_sorted = sorted(data_dict.keys())

    # === TAKE LAST SEQUENCE ===
    last_weeks = weeks_sorted[-sequence_length:]
    if last_weeks[-1][1] == 52:
        next_week = (last_weeks[-1][0], 1) 
    elif last_weeks[-1][1] == 20:
        next_week = (last_weeks[-1][0], 45) 
    else:
        next_week = (last_weeks[-1][0], last_weeks[-1][1] + 1)

    input_data = prepare_input_sequence(data_dict, last_weeks)

    if input_data is not None:
        # Shape for model
        input_data = np.expand_dims(input_data, axis=-1)
        input_data = np.expand_dims(input_data, axis=0)

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

def convertToPng(indexType, predictedWeek):
    csv_path = f"model/{indexType}/{predictedWeek}-predicted.csv"
    df = pd.read_csv(csv_path)
    index = df.values 

    if indexType == "ndvi":
        index_min, index_max = 0, 1.0
    else: 
        index_min, index_max = -1.0, 1.0

    index_norm = (index - index_min) / (index_max - index_min + 1e-8)
    index_norm = np.clip(index_norm, 0, 1)
    
    colored = cm.gist_rainbow(index_norm)[:, :, :3] * 255
    image_rgb = colored.astype(np.uint8)

    gray_mask = (index == 0.0)
    image_rgb[gray_mask] = [128, 128, 128]

    output_path = os.path.splitext(csv_path)[0] + ".png"
    Image.fromarray(image_rgb).save(output_path)

    print(f"Saved PNG: {output_path}")

def mergeBetweenIndexAndRaster(predictedWeek, indexType):
    # Load images
    background = Image.open("data/raster/latest_rgb.jpeg").convert("RGBA")
    overlay = Image.open(f'model/{indexType}/{predictedWeek}-predicted.png').convert("RGBA")

    datas = overlay.getdata()
    new_data = []
    for item in datas:

        if 100 < item[0] < 160 and 100 < item[1] < 160 and 100 < item[2] < 160:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)
    overlay.putdata(new_data)

    # Resize overlay to match background
    overlay_resized = overlay.resize(background.size)
    alpha = 0.65  # 35% visible (65% transparent)

    r, g, b, a = overlay_resized.split()

    a = a.point(lambda p: int(p * alpha))

    overlay_with_alpha = Image.merge("RGBA", (r, g, b, a))

    merged = Image.alpha_composite(background, overlay_with_alpha)

    merged.save(f"model/{indexType}/{predictedWeek}-merged.png")
        

def applyZeroMaskFromOriginal(indexType, predictedWeek):

    raw_folder = f"data/{indexType}/rawdata"
    files = [f for f in os.listdir(raw_folder) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError(f"No CSV files found in {raw_folder}")
    latest_file = max(
        files,
        key=lambda f: os.path.getmtime(os.path.join(raw_folder, f))
    )
    latest_path = os.path.join(raw_folder, latest_file)

    print(f"Using latest original file: {latest_file}")

    # === load data ===
    original = pd.read_csv(latest_path)
    predicted_path = f"model/{indexType}/{predictedWeek}-predicted.csv"
    predicted = pd.read_csv(predicted_path)

    original_values = original.iloc[:, 1:].values 
    predicted_values = predicted.values

    mask_zero = (original_values == 0)
    predicted_values[mask_zero] = 0

    predicted_fixed = pd.DataFrame(predicted_values, columns=predicted.columns)
    predicted_fixed.to_csv(predicted_path, index=False)

    print(f"Saved fixed predicted file to: {predicted_path}")