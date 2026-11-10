#!/usr/bin/env python3
"""
Quick entry point to start MediaCleaner from the repository root.
Usage:
    python run_cleaner.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from media_cleaner.run import main

if __name__ == "__main__":
    main()
