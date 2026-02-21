from flask import Blueprint, render_template, redirect, url_for
from lms.service.dashboard_service import DashboardService
from lms.service.recommendation_service import RecommendationService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("dashboard", __name__)

@bp.get("/")
def home():
    user_id = 1
    data = DashboardService.get_today(user_id)
    return render_template("dashboard.html", data=data)

@bp.post("/recommend/today")
def recommend_today():
    user_id = 1
    RecommendationService.generate_today(user_id)
    return redirect(url_for("dashboard.home"))