from flask import Blueprint, render_template

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("test_home.html", page_title="HOME")

@bp.route("/about")
def about():
    return render_template("test_home.html", page_title="소개")
