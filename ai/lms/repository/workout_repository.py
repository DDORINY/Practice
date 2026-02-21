from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class WorkoutRepository(BaseRepository):

    @staticmethod
    def create(conn: Connection, user_id: int, start_at: str, type_: str, duration_min: int,
               intensity: str, kcal_est: Optional[int], note: Optional[str], source: str="manual") -> int:
        sql = """
        INSERT INTO workout_logs
          (user_id, start_at, type, duration_min, intensity, kcal_est, note, source)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return WorkoutRepository.insert(conn, sql, (
            user_id, start_at, type_, duration_min, intensity, kcal_est, note, source
        ))