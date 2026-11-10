"""
Configuration settings for Media Cleaner Web Application.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Storage paths
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "web" / "static"
TEMPLATES_DIR = BASE_DIR / "web" / "templates"

# Ensure runtime directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Allowed extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".mpg", ".mpeg", ".webm", ".flv", ".m4v", ".3gp", ".ts"}

ALL_ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# Upload limits
MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

# Server settings
HOST = "0.0.0.0"
PORT = 8000
