from flask import Blueprint, request
import bcrypt

from lms.common.db import db_session
from lms.repository.user_repository import UserRepository
from lms.repository.profile_repository import ProfileRepository

bp = Blueprint("auth_api", __name__, url_prefix="/auth")

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "")
    name = (data.get("name") or "").strip()

    if not email or not password:
        return {"ok": False, "message": "email/password는 필수입니다."}, 400

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with db_session() as conn:
        if UserRepository.find_by_email(conn, email):
            return {"ok": False, "message": "이미 사용 중인 이메일입니다."}, 409

        user_id = UserRepository.create(
            conn,
            email=email,
            password_hash=pw_hash,
            name=name or None,
            role="user"
        )

        # 프로필 기본 row 생성(없으면 FK/조회에서 문제)
        ProfileRepository.create_empty(conn, user_id)

    return {"ok": True, "user_id": user_id}
@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "")

    if not email or not password:
        return {"ok": False, "message": "email/password는 필수입니다."}, 400

    with db_session() as conn:
        user = UserRepository.find_by_email(conn, email)

        if not user:
            return {"ok": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}, 401

        # user["password_hash"] 또는 user.password_hash 형태는 너 repo 반환 타입에 맞춰 조정
        stored_hash = user.get("password_hash") if isinstance(user, dict) else getattr(user, "password_hash", None)

        if not stored_hash:
            return {"ok": False, "message": "계정 비밀번호 정보가 없습니다. 관리자에게 문의하세요."}, 500

        ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        if not ok:
            return {"ok": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}, 401

        # ✅ JWT 쓰는 중이면 여기서 토큰 발급
        # access_token = create_access_token(identity=user["id"])
        # return {"ok": True, "access_token": access_token, "user": {...}}

        # ✅ 세션 기반이면 여기서 session 저장
        # session["user_id"] = user["id"]
        # return {"ok": True}

        return {"ok": True, "user_id": (user["id"] if isinstance(user, dict) else user.id)}