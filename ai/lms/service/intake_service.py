from __future__ import annotations
from lms.common.db import db_session
from lms.repository.intake_repository import IntakeRepository
from lms.repository.daily_summary_repository import DailyNutritionSummaryRepository

class IntakeService:
    @staticmethod
    def add_intake(user_id: int, eaten_at: str, meal_type: str, description: str,
                  kcal: int, carbs_g: float, protein_g: float, fat_g: float, sugar_g: float, sodium_mg: int) -> int:
        date_str = eaten_at[:10]  # 'YYYY-MM-DD'
        with db_session() as conn:
            log_id = IntakeRepository.create(
                conn, user_id, eaten_at, meal_type, description,
                kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg
            )
            DailyNutritionSummaryRepository.add_intake(
                conn, user_id, date_str, kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg
            )
            return log_id