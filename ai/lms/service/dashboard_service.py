from __future__ import annotations
from lms.common.db import db_session
from lms.repository.base_repository import BaseRepository

class DashboardService(BaseRepository):
    @staticmethod
    def get_today(user_id: int):
        sql = """
        SELECT *
        FROM v_today_dashboard
        WHERE user_id=%s
        """
        with db_session() as conn:
            row = DashboardService.fetchone(conn, sql, (user_id,))
            return row or {"user_id": user_id, "date": None}