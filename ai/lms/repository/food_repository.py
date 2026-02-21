from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class FoodRepository(BaseRepository):

    @staticmethod
    def create_from_ocr(conn: Connection, name: str, fields: Dict[str, Any], ocr_job_id: int, raw_text: str) -> int:
        sql = """
        INSERT INTO food_products
          (name, serving_size_g, serving_unit, kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg,
           source, ocr_job_id, raw_label_text)
        VALUES
          (%s, %s, 'g', %s, %s, %s, %s, %s, %s,
           'ocr', %s, %s)
        """
        return FoodRepository.insert(conn, sql, (
            name,
            fields.get("serving_size_g"),
            fields.get("kcal"),
            fields.get("carbs_g"),
            fields.get("protein_g"),
            fields.get("fat_g"),
            fields.get("sugar_g"),
            fields.get("sodium_mg"),
            ocr_job_id,
            raw_text
        ))