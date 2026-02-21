from __future__ import annotations

from typing import Optional
from lms.common.db import db_session
from lms.common.errors import ConflictError, NotFoundError
from lms.repository.user_repository import UserRepository
from lms.repository.profile_repository import ProfileRepository

class UserService:

    @staticmethod
    def register(email: str, password_hash: str, name: Optional[str] = None) -> int:
        with db_session() as conn:
            existing = UserRepository.find_by_email(conn, email)
            if existing:
                raise ConflictError("이미 사용 중인 이메일입니다.")

            user_id = UserRepository.create(conn, email=email, password_hash=password_hash, name=name, role="user")
            ProfileRepository.create_empty(conn, user_id)
            return user_id

    @staticmethod
    def get_user(user_id: int):
        with db_session() as conn:
            user = UserRepository.find_by_id(conn, user_id)
            if not user:
                raise NotFoundError("사용자를 찾을 수 없습니다.")
            profile = ProfileRepository.find_by_user_id(conn, user_id)
            user["profile"] = profile
            return user