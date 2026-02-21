from __future__ import annotations
from lms.common.db import db_session
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class CalendarService(BaseRepository):

    @staticmethod
    def create_appointment(user_id: int, start_at: str, end_at: str, memo: str = ""):
        with db_session() as conn:
            appt_sql = """
            INSERT INTO appointments (user_id, coach_id, start_at, end_at, status, memo)
            VALUES (%s, NULL, %s, %s, 'requested', %s)
            """
            appt_id = CalendarService.insert(conn, appt_sql, (user_id, start_at, end_at, memo))

            cal_sql = """
            INSERT INTO calendar_events (user_id, appointment_id, provider, title, description, start_at, end_at)
            VALUES (%s, %s, 'internal', '상담 예약', %s, %s, %s)
            """
            CalendarService.insert(conn, cal_sql, (user_id, appt_id, memo, start_at, end_at))
            return appt_id

    @staticmethod
    def list_events(user_id: int):
        with db_session() as conn:
            sql = """
            SELECT id, title, start_at, end_at, description
            FROM calendar_events
            WHERE user_id=%s
            ORDER BY start_at DESC
            LIMIT 50
            """
            return CalendarService.fetchall(conn, sql, (user_id,))

    @staticmethod
    def create_appointment_with_conn(
            conn: Connection,
            user_id: int,
            start_at: str,
            end_at: str,
            memo: str = "",
            title: str = "AI 추천 일정"
    ) -> int:
        # appointments
        appt_sql = """
           INSERT INTO appointments (user_id, coach_id, start_at, end_at, status, memo)
           VALUES (%s, NULL, %s, %s, 'requested', %s)
           """
        appt_id = CalendarService.insert(conn, appt_sql, (user_id, start_at, end_at, memo))

        # calendar_events
        cal_sql = """
           INSERT INTO calendar_events (user_id, appointment_id, provider, title, description, start_at, end_at)
           VALUES (%s, %s, 'internal', %s, %s, %s, %s)
           """
        CalendarService.insert(conn, cal_sql, (user_id, appt_id, title, memo, start_at, end_at))
        return appt_id

    @staticmethod
    def exists_ai_event_today(conn, user_id: int) -> bool:
        sql = """
        SELECT COUNT(*) AS cnt
        FROM calendar_events
        WHERE user_id=%s
          AND provider='internal'
          AND title LIKE 'AI:%'
          AND DATE(start_at)=CURDATE()
        """
        row = CalendarService.fetchone(conn, sql, (user_id,))
        return (row and row.get("cnt", 0) > 0)