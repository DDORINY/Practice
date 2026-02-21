from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple
from pymysql.connections import Connection

class BaseRepository:
    @staticmethod
    def fetchone(conn: Connection, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()

    @staticmethod
    def fetchall(conn: Connection, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Sequence[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

    @staticmethod
    def execute(conn: Connection, sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount

    @staticmethod
    def insert(conn: Connection, sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.lastrowid