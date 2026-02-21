from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from lms.service.prediction_service import PredictionService

bp = Blueprint("predict", __name__, url_prefix="/predict")

@bp.get("/week")
@jwt_required()
def week():
    user_id = int(get_jwt_identity())
    result = PredictionService.predict_next_7_days(user_id)
    return render_template("predict_week.html", result=result)