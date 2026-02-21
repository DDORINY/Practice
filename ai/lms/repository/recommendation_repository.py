from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class RecommendationRepository(BaseRepository):

    @staticmethod
    def upsert_today(conn: Connection, user_id: int, date_str: str,
                     remaining_kcal: Optional[int],
                     protein_gap_g: Optional[float],
                     carb_limit_g: Optional[float],
                     fat_limit_g: Optional[float],
                     sodium_warning: int,
                     coach_message: Optional[str],
                     action_plan_json: Optional[str],
                     model: Optional[str] = None,
                     prompt_version: Optional[str] = "rule-v1") -> int:
        sql = """
        INSERT INTO daily_recommendations
          (user_id, date, remaining_kcal, protein_gap_g, carb_limit_g, fat_limit_g,
           sodium_warning, coach_message, action_plan_json, model, prompt_version)
        VALUES
          (%s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          remaining_kcal=VALUES(remaining_kcal),
          protein_gap_g=VALUES(protein_gap_g),
          carb_limit_g=VALUES(carb_limit_g),
          fat_limit_g=VALUES(fat_limit_g),
          sodium_warning=VALUES(sodium_warning),
          coach_message=VALUES(coach_message),
          action_plan_json=VALUES(action_plan_json),
          model=VALUES(model),
          prompt_version=VALUES(prompt_version),
          updated_at=NOW()
        """
        return RecommendationRepository.execute(conn, sql, (
            user_id, date_str, remaining_kcal, protein_gap_g, carb_limit_g, fat_limit_g,
            sodium_warning, coach_message, action_plan_json, model, prompt_version
        ))