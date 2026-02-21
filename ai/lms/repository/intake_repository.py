from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class IntakeRepository(BaseRepository):

    @staticmethod
    def create(conn: Connection, user_id: int, eaten_at: str, meal_type: str,
               description: Optional[str],
               kcal: int, carbs_g: float, protein_g: float, fat_g: float, sugar_g: float, sodium_mg: int,
               source: str="manual") -> int:
        sql = """
        INSERT INTO intake_logs
          (user_id, eaten_at, meal_type, description, kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg, source)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return IntakeRepository.insert(conn, sql, (
            user_id, eaten_at, meal_type, description,
            kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg, source
        ))