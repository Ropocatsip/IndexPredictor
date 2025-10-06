FROM python:3.13-slim

WORKDIR /app

# ติดตั้ง system libraries ที่จำเป็นต่อ rasterio, GDAL, และ TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libexpat1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements.txt เข้ามา
COPY requirements.txt requirements.txt

# อัปเดต pip และพยายามติดตั้งจาก binary wheel ก่อน (หลีกเลี่ยงการคอมไพล์)
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --only-binary=:all: -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดเข้ามา
COPY . .

EXPOSE 8000

# รัน Flask โดยตรง (ถ้าใช้ gunicorn ให้เปลี่ยนเป็นบรรทัด CMD ที่คอมเมนต์ไว้)
CMD ["python", "app.py"]
# CMD ["gunicorn","-w","2","-k","gthread","--threads","8","-b","0.0.0.0:8000","app:app"]
