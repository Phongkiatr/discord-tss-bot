FROM python:3.11-slim

# ติดตั้ง FFmpeg (จำเป็นสำหรับ Discord Voice)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
