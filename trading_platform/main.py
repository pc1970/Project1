"""
Entry point for the Currency Trading Platform.
Run with: python main.py
Or with uvicorn: uvicorn app:app --host 0.0.0.0 --port 8080
"""
import os
import sys
import logging
import socket
import threading
import webbrowser
from pathlib import Path

# ── Path setup for bundled (PyInstaller) and dev execution ───────────────────
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path.home() / ".trading_platform" / "platform.log"),
    ],
)
logger = logging.getLogger("main")


def find_free_port(start: int = 8080, end: int = 8180) -> int:
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
    return start


def open_browser(port: int) -> None:
    import time
    time.sleep(2)
    url = f"http://localhost:{port}"
    logger.info(f"Opening browser at {url}")
    webbrowser.open(url)


def main():
    port = int(os.environ.get("TRADING_PORT", find_free_port()))
    host = os.environ.get("TRADING_HOST", "0.0.0.0")

    print("=" * 60)
    print("  CurrencyTrader Pro - Full Stack Trading Platform")
    print("=" * 60)
    print(f"  Server: http://localhost:{port}")
    print(f"  API Docs: http://localhost:{port}/docs")
    print(f"  Default login: admin / admin123")
    print(f"  Data stored at: {Path.home() / '.trading_platform'}")
    print("=" * 60)
    print("  Press Ctrl+C to stop\n")

    # Open browser after short delay
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    import uvicorn
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
        app_dir=str(BASE_DIR),
    )


if __name__ == "__main__":
    main()
