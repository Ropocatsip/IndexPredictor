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
    last_weeks = weeks_sorted[-sequence_length:]       # last 6 weeks
    if last_weeks[-1][1] == 52:
        next_week = (last_weeks[-1][0], 1) 
    elif last_weeks[-1][1] == 20:
        next_week = (last_weeks[-1][0], 45) 
    else:
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

def convertToPng(indexType):
    output_folder = f"model/{indexType}"

    # === FIND THE ONLY CSV FILE IN FOLDER ===
    csv_files = [f for f in os.listdir(output_folder) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError(f"No CSV file found in model/{indexType} folder.")
    csv_file = os.path.join(output_folder, csv_files[0])  # take the first (only) file

    # === LOAD CSV ===
    df = pd.read_csv(csv_file)
    index = df.values  # convert to numpy array

    polygon = [(88, 110), (273, 164), (274, 252), (89, 226)]
    # Create polygon mask
    mask_img = Image.new("L", (index.shape[1], index.shape[0]), 0)
    ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)
    polygon_mask = np.array(mask_img).astype(bool)  # True = inside polygon

    # === NORMALIZE to [0,1] ===
    if indexType == "ndvi":
        index_min, index_max = 0, 1.0
    else: 
        index_min, index_max = -1.0, 1.0

    index_norm = np.zeros_like(index, dtype=float)
    index_norm[polygon_mask] = (index[polygon_mask] - index_min) / (index_max - index_min + 1e-8)
    index_norm = np.clip(index_norm, 0, 1)
    # index_norm = (index - index_min) / (index_max - index_min + 1e-8)
    # index_norm = np.clip(index_norm, 0, 1)
    
    # === CONVERT TO 8-BIT RGB IMAGE ===
    colored = cm.gist_rainbow(index_norm)[:, :, :3] * 255
    image_rgb = colored.astype(np.uint8)

    # === SET BACKGROUND TO GRAY ===
    image_rgb[~polygon_mask] = [128, 128, 128]

    # === SAVE PNG ===
    base_name = os.path.splitext(csv_files[0])[0]  # remove .csv
    output_path = os.path.join(output_folder, f"{base_name}.png")
    Image.fromarray(image_rgb).save(output_path)

    print(f"Saved PNG: {output_path}")

def mergeBetweenIndexAndRaster(predictedWeek, indexType):
    # Load images
    background = Image.open("data/raster/latest_rgb.jpeg").convert("RGBA")   # your first image
    overlay = Image.open(f'model/{indexType}/{predictedWeek}-predicted.png').convert("RGBA") # your second image

    # Make gray background transparent
    datas = overlay.getdata()
    new_data = []
    for item in datas:
        # Detect gray (approx 128,128,128, adjust thresholds if needed)
        if 100 < item[0] < 160 and 100 < item[1] < 160 and 100 < item[2] < 160:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)
    overlay.putdata(new_data)

    # Resize overlay to match background
    overlay_resized = overlay.resize(background.size)
    alpha = 0.8  # 20% visible (80% transparent)
    # Create new image with reduced alpha
    r, g, b, a = overlay_resized.split()
    # Reduce alpha channel
    a = a.point(lambda p: int(p * alpha))
    # Merge back
    overlay_with_alpha = Image.merge("RGBA", (r, g, b, a))

    # Merge images
    merged = Image.alpha_composite(background, overlay_with_alpha)

    # Save result
    merged.save(f"model/{indexType}/{predictedWeek}-merged.png")
        
