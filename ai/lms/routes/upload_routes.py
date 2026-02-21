from flask import Blueprint, render_template, request
from lms.service.upload_service import UploadService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("upload", __name__, url_prefix="/upload")

@bp.get("/")
def upload_home():
    return render_template("upload_home.html")

@bp.get("/nutrition")
def nutrition_form():
    return render_template("upload_nutrition.html")

@bp.post("/nutrition")
def nutrition_upload():
    user_id = 1
    f = request.files.get("image")
    product_name = request.form.get("product_name") or "OCR 제품"
    try:
        result = UploadService.upload_nutrition_label(user_id, f, product_name)
        return render_template("upload_result.html", title="영양성분표 분석 결과", result=result)
    except Exception as e:
        return render_template("upload_result.html", title="영양성분표 분석 실패", error=str(e), result=None)

@bp.get("/inbody")
def inbody_form():
    return render_template("upload_inbody.html")

@bp.post("/inbody")
def inbody_upload():
    user_id = 1
    f = request.files.get("image")
    measured_at = request.form.get("measured_at")  # 'YYYY-MM-DD HH:MM:SS'
    try:
        result = UploadService.upload_inbody(user_id, f, measured_at)
        return render_template("upload_result.html", title="인바디 분석 결과", result=result)
    except Exception as e:
        return render_template("upload_result.html", title="인바디 분석 실패", error=str(e), result=None)