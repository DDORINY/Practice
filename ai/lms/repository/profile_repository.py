from __future__ import annotations

from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class ProfileRepository(BaseRepository):

    @staticmethod
    def find_by_user_id(conn: Connection, user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT *
        FROM user_profile
        WHERE user_id=%s
        """
        return ProfileRepository.fetchone(conn, sql, (user_id,))

    @staticmethod
    def create_empty(conn: Connection, user_id: int) -> int:
        """
        회원 생성 직후 기본 프로필 row를 만들고 시작하면 편함.
        """
        sql = """
        INSERT INTO user_profile (user_id)
        VALUES (%s)
        """
        return ProfileRepository.execute(conn, sql, (user_id,))

    @staticmethod
    def upsert_profile(conn: Connection, user_id: int, data: Dict[str, Any]) -> int:
        """
        필요한 필드만 업데이트 가능하게 동적 UPDATE.
        허용 필드만 whitelist로 제한.
        """
        allowed = {
            "sex", "birth_year", "height_cm",
            "activity_level", "diet_preference",
            "allergies_json", "avoid_foods_json",
            "goal_type", "goal_weight_kg", "goal_start_date", "goal_end_date",
            "target_kcal", "target_protein_g", "target_carbs_g", "target_fat_g", "target_sodium_mg",
        }

        items = [(k, v) for k, v in data.items() if k in allowed]
        if not items:
            return 0

        sets = ", ".join([f"{k}=%s" for k, _ in items])
        params = [v for _, v in items]
        params.append(user_id)

        sql = f"""
        UPDATE user_profile
        SET {sets}
        WHERE user_id=%s
        """
        return ProfileRepository.execute(conn, sql, tuple(params))

    @staticmethod
    def get_targets(conn: Connection, user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT
          target_kcal, target_protein_g, target_carbs_g, target_fat_g, target_sodium_mg
        FROM user_profile
        WHERE user_id=%s
        """
        return ProfileRepository.fetchone(conn, sql, (user_id,))