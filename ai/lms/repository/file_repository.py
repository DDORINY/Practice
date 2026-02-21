from __future__ import annotations
from typing import Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class FileRepository(BaseRepository):

    @staticmethod
    def create(conn: Connection, user_id: int, file_type: str, file_path: str,
               original_name: Optional[str], mime_type: Optional[str], file_size: Optional[int]) -> int:
        sql = """
        INSERT INTO uploaded_files (user_id, file_type, storage, file_path, original_name, mime_type, file_size)
        VALUES (%s, %s, 'local', %s, %s, %s, %s)
        """
        return FileRepository.insert(conn, sql, (user_id, file_type, file_path, original_name, mime_type, file_size))