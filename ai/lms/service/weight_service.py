from __future__ import annotations
from typing import Optional
from lms.common.db import db_session
from lms.repository.weight_repository import WeightRepository

class WeightService:
    @staticmethod
    def add_weight(user_id: int, measured_at: str, weight_kg: float, note: Optional[str]=None) -> int:
        with db_session() as conn:
            return WeightRepository.create(conn, user_id, measured_at, weight_kg, note)

    @staticmethod
    def recent(user_id: int, limit: int=14):
        with db_session() as conn:
            return WeightRepository.list_recent(conn, user_id, limit)