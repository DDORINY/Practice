from __future__ import annotations
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class DailyActivitySummaryRepository(BaseRepository):

    @staticmethod
    def add_burn(conn: Connection, user_id: int, date_str: str, kcal_burn: int) -> int:
        sql = """
        INSERT INTO daily_activity_summary (user_id, date, total_kcal_burn)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
          total_kcal_burn = total_kcal_burn + VALUES(total_kcal_burn)
        """
        return DailyActivitySummaryRepository.execute(conn, sql, (user_id, date_str, kcal_burn))