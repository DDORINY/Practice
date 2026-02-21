from __future__ import annotations
from typing import Any, Dict, Optional, Sequence
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class WeightRepository(BaseRepository):

    @staticmethod
    def create(conn: Connection, user_id: int, measured_at: str, weight_kg: float, note: Optional[str], source: str="manual") -> int:
        sql = """
        INSERT INTO weight_logs (user_id, measured_at, weight_kg, note, source)
        VALUES (%s, %s, %s, %s, %s)
        """
        return WeightRepository.insert(conn, sql, (user_id, measured_at, weight_kg, note, source))

    @staticmethod
    def list_recent(conn: Connection, user_id: int, limit: int=14) -> Sequence[Dict[str, Any]]:
        sql = """
        SELECT id, measured_at, weight_kg, note
        FROM weight_logs
        WHERE user_id=%s AND deleted_at IS NULL
        ORDER BY measured_at DESC
        LIMIT %s
        """
        return WeightRepository.fetchall(conn, sql, (user_id, limit))

    @staticmethod
    def latest(conn: Connection, user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, measured_at, weight_kg
        FROM weight_logs
        WHERE user_id=%s AND deleted_at IS NULL
        ORDER BY measured_at DESC
        LIMIT 1
        """
        return WeightRepository.fetchone(conn, sql, (user_id,))

    @staticmethod
    def list_last_days(conn: Connection, user_id: int, days: int = 14):
        sql = """
        SELECT DATE(measured_at) AS d, AVG(weight_kg) AS w
        FROM weight_logs
        WHERE user_id=%s AND deleted_at IS NULL
          AND measured_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(measured_at)
        ORDER BY d ASC
        """
        return WeightRepository.fetchall(conn, sql, (user_id, days))