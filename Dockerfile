FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg build-essential libsndfile1 && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers=1", "--threads=4"]
