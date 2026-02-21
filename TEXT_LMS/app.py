import os
from flask import Flask
from config import Config

from lms.routes.main_routes import bp as main_bp
from lms.routes.member_routes import bp as member_bp
from lms.routes.admin_routes import bp as admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🔥 업로드 폴더 자동 생성 (시험 중 에러 방지)
    os.makedirs(app.config["UPLOAD_PROFILE_DIR"], exist_ok=True)

    # Blueprint 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
