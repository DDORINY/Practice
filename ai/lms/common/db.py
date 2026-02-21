from __future__ import annotations

from contextlib import contextmanager
import pymysql
from pymysql.connections import Connection
from lms.config import Config

def get_connection() -> Connection:
    """
    매 호출마다 새 연결 생성(단순/안정).
    트래픽 늘면 pool로 교체 가능.
    """
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET,
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )

@contextmanager
def db_session():
    """
    with db_session() as conn:
        ... cursor execute ...
    자동 commit/rollback + close
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()