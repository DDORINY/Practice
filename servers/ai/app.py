import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from servers.ai.aistream_app import app, socketio


if __name__ == "__main__":
    host = os.getenv("AI_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("AI_SERVER_PORT", os.getenv("AISTREAM_PORT", "5001")))
    debug = os.getenv("AI_SERVER_DEBUG", "0") == "1"
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
