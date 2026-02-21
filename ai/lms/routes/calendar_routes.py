from flask import Blueprint, render_template, request, redirect, url_for
from lms.service.calendar_service import CalendarService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("calendar", __name__, url_prefix="/calendar")

@bp.get("/")
def calendar_home():
    user_id = 1
    events = CalendarService.list_events(user_id)
    return render_template("calendar.html", events=events)

@bp.post("/new")
def calendar_new():
    user_id = 1
    start_at = request.form.get("start_at")
    end_at = request.form.get("end_at")
    memo = request.form.get("memo") or ""
    CalendarService.create_appointment(user_id, start_at, end_at, memo)
    return redirect(url_for("calendar.calendar_home"))