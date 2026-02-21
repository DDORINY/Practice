from flask import Blueprint, render_template

bp = Blueprint("auth_pages", __name__)

@bp.get("/login")
def login_page():
    return render_template("login.html")

@bp.get("/register")
def register_page():
    return render_template("register.html")