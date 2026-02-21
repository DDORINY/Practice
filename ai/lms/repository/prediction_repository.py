from __future__ import annotations
from typing import Any, Dict, List
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class PredictionRepository(BaseRepository):

    @staticmethod
    def get_weight_series(conn: Connection, user_id: int, days: int = 21) -> List[Dict[str, Any]]:
        sql = """
        SELECT DATE(measured_at) AS d, AVG(weight_kg) AS w
        FROM weight_logs
        WHERE user_id=%s AND deleted_at IS NULL
          AND measured_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(measured_at)
        ORDER BY d ASC
        """
        return list(PredictionRepository.fetchall(conn, sql, (user_id, days)))

    @staticmethod
    def get_daily_balance(conn: Connection, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        sql = """
        SELECT
          dns.date AS d,
          dns.total_kcal AS intake_kcal,
          COALESCE(das.total_kcal_burn, 0) AS burn_kcal
        FROM daily_nutrition_summary dns
        LEFT JOIN daily_activity_summary das
          ON das.user_id=dns.user_id AND das.date=dns.date
        WHERE dns.user_id=%s
          AND dns.date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY dns.date ASC
        """
        return list(PredictionRepository.fetchall(conn, sql, (user_id, days)))