from __future__ import annotations
from typing import Optional
from lms.common.db import db_session
from lms.repository.workout_repository import WorkoutRepository
from lms.repository.daily_activity_repository import DailyActivitySummaryRepository

class WorkoutService:
    @staticmethod
    def add_workout(user_id: int, start_at: str, type_: str, duration_min: int, intensity: str,
                    kcal_est: Optional[int], note: Optional[str]) -> int:
        date_str = start_at[:10]
        with db_session() as conn:
            log_id = WorkoutRepository.create(conn, user_id, start_at, type_, duration_min, intensity, kcal_est, note)
            if kcal_est is not None:
                DailyActivitySummaryRepository.add_burn(conn, user_id, date_str, int(kcal_est))
            return log_id