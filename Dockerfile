FROM python:3.11-slim

# System dependencies for OpenCV, FFmpeg and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for caching
COPY media_cleaner/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

# Ensure runtime upload/output directories exist
RUN mkdir -p /app/media_cleaner/uploads /app/media_cleaner/outputs

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Expose standard port
EXPOSE 8000

# Render provides the $PORT environment variable dynamically
CMD ["sh", "-c", "python media_cleaner/run.py --no-browser --port=${PORT:-8000}"]
