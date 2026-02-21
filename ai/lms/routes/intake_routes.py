from flask import Blueprint, render_template, request, redirect, url_for
from lms.service.intake_service import IntakeService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("intake", __name__, url_prefix="/intake")

@bp.get("/new")
def new():
    return render_template("intake_form.html")

@bp.post("/new")
def create():
    user_id = 1
    eaten_at = request.form.get("eaten_at")
    meal_type = request.form.get("meal_type") or "unknown"
    description = request.form.get("description") or ""
    kcal = int(request.form.get("kcal") or 0)
    carbs_g = float(request.form.get("carbs_g") or 0)
    protein_g = float(request.form.get("protein_g") or 0)
    fat_g = float(request.form.get("fat_g") or 0)
    sugar_g = float(request.form.get("sugar_g") or 0)
    sodium_mg = int(request.form.get("sodium_mg") or 0)

    IntakeService.add_intake(user_id, eaten_at, meal_type, description,
                             kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg)
    return redirect(url_for("dashboard.home"))