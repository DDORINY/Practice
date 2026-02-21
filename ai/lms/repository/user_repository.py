from __future__ import annotations

from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class UserRepository(BaseRepository):

    @staticmethod
    def find_by_id(conn: Connection, user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, email, name, role, is_active, last_login_at, created_at, updated_at
        FROM users
        WHERE id=%s AND deleted_at IS NULL
        """
        return UserRepository.fetchone(conn, sql, (user_id,))

    @staticmethod
    def find_by_email(conn: Connection, email: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, email, password_hash, name, role, is_active, last_login_at, created_at, updated_at
        FROM users
        WHERE email=%s AND deleted_at IS NULL
        """
        return UserRepository.fetchone(conn, sql, (email,))

    @staticmethod
    def create(conn: Connection, email: str, password_hash: str, name: Optional[str] = None, role: str = "user") -> int:
        sql = """
        INSERT INTO users (email, password_hash, name, role)
        VALUES (%s, %s, %s, %s)
        """
        return UserRepository.insert(conn, sql, (email, password_hash, name, role))

    @staticmethod
    def update_last_login(conn: Connection, user_id: int) -> int:
        sql = """
        UPDATE users
        SET last_login_at = NOW()
        WHERE id=%s AND deleted_at IS NULL
        """
        return UserRepository.execute(conn, sql, (user_id,))

    @staticmethod
    def soft_delete(conn: Connection, user_id: int) -> int:
        sql = """
        UPDATE users
        SET deleted_at = NOW(), is_active=0
        WHERE id=%s AND deleted_at IS NULL
        """
        return UserRepository.execute(conn, sql, (user_id,))