from flask import Blueprint, render_template, request, redirect, url_for, flash
from lms.common.auth import Auth
from lms.repository.member_repo import MemberRepository
from lms.service.admin_service import AdminService
from lms.common.utils import mask_phone, mask_email, mask_address

bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_guard():
    if not Auth.is_login() or not Auth.is_admin():
        flash("권한이 없습니다.", "danger")
        return False
    return True

@bp.route("/dashboard")
def dashboard():
    if not admin_guard():
        return redirect(url_for("member.login"))
    stats = AdminService.get_dashboard_stats()
    return render_template("admin/dashboard.html", stats=stats)

@bp.route("/members")
def members():
    if not admin_guard():
        return redirect(url_for("member.login"))

    mode = request.args.get("mode", "all")
    q = (request.args.get("q") or "").strip()

    active = None
    if mode == "active": active = 1
    if mode == "inactive": active = 0

    rows = MemberRepository.list_members(active=active, keyword=q)

    # 관리자 화면은 마스킹 적용해서 템플릿에 전달
    members = []
    for r in rows:
        members.append({
            "id": r["id"],
            "uid": r["uid"],
            "name": r["name"],
            "phone": mask_phone(r["phone"]),
            "email": mask_email(r["email"]),
            "address": mask_address(r["address"]),
            "active": r["active"],
            "created_at": r["created_at"],
        })

    return render_template("admin/members_list.html", members=members, mode=mode, q=q)

@bp.route("/members/<int:member_id>")
def member_detail(member_id):
    if not admin_guard():
        return redirect(url_for("member.login"))

    r = MemberRepository.find_by_id(member_id)
    if not r:
        flash("회원이 존재하지 않습니다.", "danger")
        return redirect(url_for("admin.members"))

    m = {
        "id": r["id"],
        "uid": r["uid"],
        "name": r["name"],
        "phone_masked": mask_phone(r["phone"]),
        "email_masked": mask_email(r["email"]),
        "address_masked": mask_address(r["address"]),
        "rrn_masked": "******-*******",   # 원문 저장 안 함
        "birthdate": r["birthdate"],
        "active": r["active"],
        "created_at": r["created_at"],
        "last_login_at": r.get("last_login_at"),
    }
    return render_template("admin/member_detail.html", m=m)

@bp.route("/members/<int:member_id>/disable", methods=["POST"])
def member_disable(member_id):
    if not admin_guard():
        return redirect(url_for("member.login"))
    ok = MemberRepository.soft_delete(member_id)
    flash("비활성 처리 완료" if ok else "처리 실패", "success" if ok else "danger")
    return redirect(url_for("admin.members"))
