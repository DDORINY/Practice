from __future__ import annotations
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class ChatRepository(BaseRepository):

    @staticmethod
    def create_session(conn, user_id: int) -> int:
        sql = """
        INSERT INTO chat_sessions (user_id)
        VALUES (%s)
        """
        return ChatRepository.insert(conn, sql, (user_id,))

    @staticmethod
    def add_message(conn, session_id: int, role: str, content: str, model: str = None):
        sql = """
        INSERT INTO chat_messages (session_id, role, content, model)
        VALUES (%s, %s, %s, %s)
        """
        return ChatRepository.insert(conn, sql, (session_id, role, content, model))

    @staticmethod
    def get_latest_session(conn, user_id: int):
        sql = """
        SELECT id
        FROM chat_sessions
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
        """
        return ChatRepository.fetchone(conn, sql, (user_id,))

    @staticmethod
    def update_summary(conn, session_id: int, summary: str):
        sql = """
        UPDATE chat_sessions
        SET summary=%s, updated_at=NOW()
        WHERE id=%s
        """
        return ChatRepository.execute(conn, sql, (summary, session_id))