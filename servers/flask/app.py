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

if os.getenv("SQLITE_DB_PATH") and not os.getenv("DATABASE_URL"):
    db_path = Path(os.getenv("SQLITE_DB_PATH")).resolve()
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from servers.flask.apps.app import create_app


app = create_app(os.getenv("FLASK_CONFIG", "local"))


if __name__ == "__main__":
    host = os.getenv("FLASK_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_SERVER_PORT", "5050"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
