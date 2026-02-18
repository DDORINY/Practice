from flask import session
# 회원관리용 인증 권한 설정
class Auth:
    @staticmethod
    def login(member: dict):
        session["user_id"] = member["id"]
        session["user_uid"] = member["uid"]
        session["user_name"] = member["name"]
        session["user_role"] = member["role"]

    @staticmethod
    def logout():
        session.clear()

    @staticmethod
    def is_login() -> bool:
        return bool(session.get("user_id"))

    @staticmethod
    def is_admin() -> bool:
        return session.get("user_role") == "ADMIN"
