import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from lms.config import Config
from lms.routes import register_routes


def create_app() -> Flask:
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    # 🔐 기본 설정
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Authorization: Bearer <token>

    # ⏳ 토큰 만료 (선택)
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)

    # 🔐 JWT 초기화
    jwt = JWTManager(app)

    # 🔴 토큰 에러 핸들러 (프론트에서 처리하기 쉽게 JSON 반환)
    @jwt.unauthorized_loader
    def unauthorized_callback(err):
        return jsonify({"ok": False, "message": "토큰이 필요합니다."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err):
        return jsonify({"ok": False, "message": "유효하지 않은 토큰입니다."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"ok": False, "message": "토큰이 만료되었습니다."}), 401

    register_routes(app)
    return app