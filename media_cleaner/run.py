#!/usr/bin/env python3
"""
MediaCleaner runner script.
Starts FastAPI server using uvicorn and opens default web browser.
Automatically detects occupied ports and chooses the next available port.
"""

import sys
import socket
import webbrowser
import threading
import time
from pathlib import Path
import uvicorn

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT.parent))

from media_cleaner.web.config import PORT


def is_port_busy(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a TCP port can be bound to."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return False  # Free
        except OSError:
            return True   # Occupied


def find_available_port(start_port: int = 8000, max_tries: int = 25) -> int:
    """Find the first open TCP port starting from start_port."""
    for p in range(start_port, start_port + max_tries):
        if not is_port_busy(p):
            return p
    return start_port


def open_browser(url: str, delay: float = 1.0):
    """Open default browser after server initializes."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    # 1. Custom port argument support (e.g. --port=8080 or 8080)
    target_port = None
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            target_port = int(arg.split("=")[1])
        elif arg.isdigit() and len(arg) >= 4:
            target_port = int(arg)

    if not target_port:
        target_port = find_available_port(PORT)

    local_url = f"http://127.0.0.1:{target_port}"
    localhost_url = f"http://localhost:{target_port}"

    print("=" * 68)
    print("✨ MediaCleaner — Video va Rasmlarni Tozalash Ilovasi ✨")
    if target_port != PORT:
        print(f"ℹ️  Eslatma: {PORT}-port boshqa jarayon tomonidan band.")
        print(f"👉 Yangi bo'sh port tanlandi: {target_port}")
    print(f"🚀 Asosiy havola:    {local_url}")
    print(f"🌐 Muqobil havola:  {localhost_url}")
    print("⏹️  To'xtatish uchun: Ctrl + C bosing")
    print("=" * 68)

    # Auto-open browser using reliable 127.0.0.1 address
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()

    uvicorn.run(
        "media_cleaner.web.app:app",
        host="0.0.0.0",
        port=target_port,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()
