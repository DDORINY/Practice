from pathlib import Path

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from servers.flask.apps.config import config

db = SQLAlchemy()
csrf = CSRFProtect()

# LoginManager를 인스턴스화한다.
login_manager = LoginManager() 
# login_view 속성에 미로그인 시 리다이렉트하는 앤드포인트를 지정한다.
login_manager.login_view = "auth.signup"
# login_message 속성에 로그인 후에 표시할 메세지를 지정한다.
# 여기에서는 아무것도 표시하지 않도록 공백을 지정한다.
login_manager.login_message =""


def create_app(config_key):
    app = Flask(__name__)

    app.config.from_object(config[config_key])


    db.init_app(app)
    csrf.init_app(app)
    Migrate(app, db)

    # login_manager를 애플리케이션과 연계한다.
    login_manager.init_app(app)

    from servers.flask.apps.crud import models
    from servers.flask.apps.crud import views as crud_views
    from servers.flask.apps.auth import views as auth_views
    from servers.flask.apps.detector import views as dt_views

    app.register_blueprint(crud_views.crud, url_prefix="/crud")
    app.register_blueprint(auth_views.auth, url_prefix="/auth")
    app.register_blueprint(dt_views.dt)

    # 커스텀 오류 화면을 등록한다.
    app.register_error_handler(404, pape_not_found)
    app.register_error_handler(500, internal_server_error)

    return app

# 등록한 엔드포인트명의 함수를 작성하고, 404 오류나 500오류가 발생했을 때에 지정한 HTML을 반환한다
def pape_not_found(e):
    """404 Not Found"""
    return render_template("detector/404.html"),404

def internal_server_error(e):
    """500 Internal Serveer Error"""
    return render_template("detector/500.html"),500
