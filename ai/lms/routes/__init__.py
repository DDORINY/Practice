from lms.routes.dashboard_routes import bp as dashboard_bp
from lms.routes.weight_routes import bp as weight_bp
from lms.routes.intake_routes import bp as intake_bp
from lms.routes.workout_routes import bp as workout_bp
from lms.routes.chat_routes import bp as chat_bp
from lms.routes.upload_routes import bp as upload_bp
from lms.routes.calendar_routes import bp as calendar_bp
from lms.routes.prediction_routes import bp as predict_bp
from lms.routes.auth_routes import bp as auth_pages_bp
from lms.routes.auth_api_routes import bp as auth_api_bp


def register_routes(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(weight_bp)
    app.register_blueprint(intake_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(auth_pages_bp)
    app.register_blueprint(auth_api_bp)
