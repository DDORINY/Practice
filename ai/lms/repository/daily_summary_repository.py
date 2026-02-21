from __future__ import annotations
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class DailyNutritionSummaryRepository(BaseRepository):

    @staticmethod
    def add_intake(conn: Connection, user_id: int, date_str: str,
                  kcal: int, carbs_g: float, protein_g: float, fat_g: float, sugar_g: float, sodium_mg: int) -> int:
        sql = """
        INSERT INTO daily_nutrition_summary
          (user_id, date, total_kcal, total_carbs_g, total_protein_g, total_fat_g, total_sugar_g, total_sodium_mg)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          total_kcal = total_kcal + VALUES(total_kcal),
          total_carbs_g = total_carbs_g + VALUES(total_carbs_g),
          total_protein_g = total_protein_g + VALUES(total_protein_g),
          total_fat_g = total_fat_g + VALUES(total_fat_g),
          total_sugar_g = total_sugar_g + VALUES(total_sugar_g),
          total_sodium_mg = total_sodium_mg + VALUES(total_sodium_mg)
        """
        return DailyNutritionSummaryRepository.execute(conn, sql, (
            user_id, date_str, kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg
        ))