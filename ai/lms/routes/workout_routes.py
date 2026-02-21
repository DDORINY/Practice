from flask import Blueprint, render_template, request, redirect, url_for
from lms.service.workout_service import WorkoutService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("workout", __name__, url_prefix="/workout")

@bp.get("/new")
def new():
    return render_template("workout_form.html")

@bp.post("/new")
def create():
    user_id = 1
    start_at = request.form.get("start_at")
    type_ = request.form.get("type") or "other"
    duration_min = int(request.form.get("duration_min") or 0)
    intensity = request.form.get("intensity") or "moderate"
    kcal_est = request.form.get("kcal_est")
    kcal_est = int(kcal_est) if kcal_est not in (None, "",) else None
    note = request.form.get("note") or None

    WorkoutService.add_workout(user_id, start_at, type_, duration_min, intensity, kcal_est, note)
    return redirect(url_for("dashboard.home"))