import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(path=None):
        return False


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

app = Flask(__name__)


def configured_rtsp_url():
    return os.getenv("AISTREAM_RTSP_URL", "")


def masked_url(url):
    parsed = urlsplit(url)
    if not parsed.password:
        return url

    username = parsed.username or ""
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{username}:***@{hostname}{port}{parsed.path}"


def tcp_reachable(url, timeout=2):
    parsed = urlsplit(url)
    if not parsed.hostname:
        return False, "missing host"

    port = parsed.port or 554
    try:
        with socket.create_connection((parsed.hostname, port), timeout=timeout):
            return True, "open"
    except OSError as exc:
        return False, str(exc)


@app.get("/")
@app.get("/health")
def health():
    rtsp_url = configured_rtsp_url()
    reachable, message = tcp_reachable(rtsp_url) if rtsp_url else (
        False,
        "AISTREAM_RTSP_URL is not set",
    )

    return {
        "status": "ok",
        "rtsp_url": masked_url(rtsp_url),
        "tcp_reachable": reachable,
        "message": message,
    }


if __name__ == "__main__":
    host = os.getenv("IPCAM_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("IPCAM_SERVER_PORT", "5003"))
    debug = os.getenv("IPCAM_SERVER_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
