from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from lms.service.chat_service import ChatService

bp = Blueprint("chat", __name__, url_prefix="/chat")

# ✅ 페이지: /chat/ 로 열림
@bp.get("/")
def chat_page():
    return render_template("chat.html")

# ✅ API: /chat/api 로 호출
@bp.post("/api")
@jwt_required()
def chat_api():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    msg = (data.get("message") or "").strip()
    if not msg:
        return {"ok": False, "message": "message가 필요합니다."}, 400

    return ChatService.chat(user_id, msg)