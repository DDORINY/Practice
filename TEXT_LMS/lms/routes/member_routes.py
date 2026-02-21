from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lms.common.auth import Auth
from lms.common.upload import save_profile_image
from lms.repository.member_repo import MemberRepository
from lms.service.member_service import MemberService

bp = Blueprint("member", __name__, url_prefix="/member")

@bp.route("/join", methods=["GET","POST"])
def join():
    if request.method == "GET":
        return render_template("member/join.html")

    try:
        profile_img = save_profile_image(request.files.get("profile_img"))
    except Exception:
        profile_img = None
        flash("프로필 이미지는 png/jpg/jpeg/webp만 가능합니다.", "warning")

    ok, msg = MemberService.join(request.form, profile_img)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("member.login")) if ok else redirect(url_for("member.join"))

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("member/login.html")

    ok, member, msg = MemberService.login(request.form.get("uid"), request.form.get("pw"))
    if not ok:
        flash(msg, "danger")
        return redirect(url_for("member.login"))

    Auth.login(member)
    flash("로그인 되었습니다.", "success")
    return redirect(url_for("member.mypage"))

@bp.route("/logout")
def logout():
    Auth.logout()
    flash("로그아웃 되었습니다.", "success")
    return redirect(url_for("main.index"))

@bp.route("/find-id", methods=["GET","POST"])
def find_id():
    result_uid = None
    if request.method == "POST":
        result_uid = MemberService.find_id(request.form.get("name"), request.form.get("email"))
        flash("조회 결과를 확인하세요." if result_uid else "일치하는 정보가 없습니다.", "info")
    return render_template("member/find_id.html", result_uid=result_uid)

@bp.route("/find-pw", methods=["GET","POST"])
def find_pw():
    # 토큰 테이블 붙이기 전: 안내만 (다음 단계에서 구현)
    reset_message = None
    if request.method == "POST":
        reset_message = "비밀번호 재설정 기능은 토큰 방식으로 다음 단계에서 연결됩니다."
        flash(reset_message, "info")
    return render_template("member/find_pw.html", reset_message=reset_message)

@bp.route("/mypage")
def mypage():
    if not Auth.is_login():
        return redirect(url_for("member.login"))
    user = MemberRepository.find_by_id(session["user_id"])
    return render_template("member/mypage.html", user=user, inquiries=[])

@bp.route("/edit", methods=["GET","POST"])
def edit():
    if not Auth.is_login():
        return redirect(url_for("member.login"))

    user = MemberRepository.find_by_id(session["user_id"])

    if request.method == "GET":
        return render_template("member/edit.html", user=user)

    try:
        profile_img = save_profile_image(request.files.get("profile_img"))
    except Exception:
        profile_img = None
        flash("프로필 이미지는 png/jpg/jpeg/webp만 가능합니다.", "warning")

    name = (request.form.get("name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    address = (request.form.get("address") or "").strip()
    email = (request.form.get("email") or "").strip()

    ok = MemberRepository.update_profile(session["user_id"], name, phone, address, email, profile_img)
    flash("수정 완료" if ok else "수정 실패", "success" if ok else "danger")
    return redirect(url_for("member.mypage"))

@bp.route("/withdraw", methods=["POST"])
def withdraw():
    if not Auth.is_login():
        return redirect(url_for("member.login"))
    ok = MemberRepository.soft_delete(session["user_id"])
    Auth.logout()
    flash("탈퇴 처리되었습니다. (1년 후 자동 삭제)", "success" if ok else "danger")
    return redirect(url_for("member.login"))
