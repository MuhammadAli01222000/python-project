FROM python:3.11-slim

# System dependencies for OpenCV and multimedia processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/media_cleaner

# Create runtime directories
RUN mkdir -p /app/media_cleaner/uploads /app/media_cleaner/outputs

ENV PYTHONPATH="/app"
EXPOSE 8000

CMD ["python", "media_cleaner/run.py", "--no-browser"]
