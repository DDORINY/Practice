from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class DailyQueryRepository(BaseRepository):

    @staticmethod
    def get_today_nutrition(conn: Connection, user_id: int) -> Dict[str, Any]:
        sql = """
        SELECT
          total_kcal, total_carbs_g, total_protein_g, total_fat_g, total_sugar_g, total_sodium_mg
        FROM daily_nutrition_summary
        WHERE user_id=%s AND date=CURDATE()
        """
        row = DailyQueryRepository.fetchone(conn, sql, (user_id,))
        return row or {
            "total_kcal": 0, "total_carbs_g": 0, "total_protein_g": 0,
            "total_fat_g": 0, "total_sugar_g": 0, "total_sodium_mg": 0
        }

    @staticmethod
    def get_today_activity(conn: Connection, user_id: int) -> Dict[str, Any]:
        sql = """
        SELECT total_kcal_burn, steps
        FROM daily_activity_summary
        WHERE user_id=%s AND date=CURDATE()
        """
        row = DailyQueryRepository.fetchone(conn, sql, (user_id,))
        return row or {"total_kcal_burn": 0, "steps": None}