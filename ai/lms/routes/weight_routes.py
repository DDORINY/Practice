from flask import Blueprint, render_template, request, redirect, url_for
from lms.service.weight_service import WeightService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("weight", __name__, url_prefix="/weight")

@bp.get("/new")
@jwt_required()
def new():
    return render_template("weight_form.html")

@bp.post("/new")
@jwt_required()
def create():
    user_id = 1
    measured_at = request.form.get("measured_at")  # 'YYYY-MM-DD HH:MM:SS'
    weight_kg = float(request.form.get("weight_kg"))
    note = request.form.get("note") or None
    WeightService.add_weight(user_id, measured_at, weight_kg, note)
    return redirect(url_for("dashboard.home"))
@bp.get("/trend")
@jwt_required()
def trend():
    from lms.repository.weight_repository import WeightRepository
    from lms.common.db import db_session

    user_id = 1
    with db_session() as conn:
        rows = WeightRepository.list_last_days(conn, user_id, 30)

    dates = [r["d"].strftime("%Y-%m-%d") for r in rows]
    weights = [float(r["w"]) if r["w"] is not None else None for r in rows]

    return render_template("weight_trend.html", dates=dates, weights=weights)