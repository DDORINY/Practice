import os
import sqlite3
import sys
from pathlib import Path

from flask import Flask

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

DEFAULT_DB_PATH = ROOT_DIR / "local.sqlite"
DB_PATH = Path(os.getenv("SQLITE_DB_PATH", DEFAULT_DB_PATH)).resolve()

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

app = Flask(__name__)


def get_tables():
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "select name from sqlite_master where type = 'table' order by name"
        ).fetchall()
    return [row[0] for row in rows]


@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": str(DB_PATH),
        "exists": DB_PATH.exists(),
        "tables": get_tables(),
    }


@app.cli.command("init")
def init_db():
    from servers.flask.apps.app import create_app, db

    flask_app = create_app(os.getenv("FLASK_CONFIG", "local"))
    with flask_app.app_context():
        db.create_all()
    print(f"Database initialized: {DB_PATH}")


if __name__ == "__main__":
    host = os.getenv("DB_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("DB_SERVER_PORT", "5002"))
    debug = os.getenv("DB_SERVER_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
