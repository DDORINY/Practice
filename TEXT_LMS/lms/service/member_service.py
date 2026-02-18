from werkzeug.security import generate_password_hash, check_password_hash
from lms.repository.member_repo import MemberRepository
from lms.common.utils import rrn_to_birthdate

class MemberService:
    @staticmethod
    def join(form: dict, profile_img_filename: str|None):
        uid = (form.get("uid") or "").strip()
        pw = (form.get("pw") or "").strip()
        pw2 = (form.get("pw_confirm") or "").strip()
        name = (form.get("name") or "").strip()
        phone = (form.get("phone") or "").strip()
        email = (form.get("email") or "").strip()
        address = (form.get("address") or "").strip()
        rrn = (form.get("rrn") or "").strip()
        agreed = form.get("retention_agreed")

        if not all([uid, pw, pw2, name, phone, email, address, rrn]):
            return (False, "필수 항목을 입력하세요.")
        if pw != pw2:
            return (False, "비밀번호 확인이 일치하지 않습니다.")
        if not agreed:
            return (False, "개인정보 보관 안내에 동의해야 가입할 수 있습니다.")

        if MemberRepository.find_by_uid(uid):
            return (False, "이미 사용중인 아이디입니다.")

        try:
            birthdate = rrn_to_birthdate(rrn)
        except Exception:
            return (False, "주민번호 형식이 올바르지 않습니다.")

        member = {
            "uid": uid,
            "pw_hash": generate_password_hash(pw),
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "birthdate": birthdate,
            "retention_agreed": 1,
            "role": "USER",
            "profile_img": profile_img_filename
        }

        ok = MemberRepository.insert(member)
        return (ok, "가입 완료" if ok else "가입 실패")

    @staticmethod
    def login(uid: str, pw: str):
        member = MemberRepository.find_by_uid((uid or "").strip())
        if not member:
            return (False, None, "아이디/비밀번호 오류")
        if member["active"] == 0:
            return (False, None, "비활성(탈퇴) 계정입니다.")
        if not check_password_hash(member["pw_hash"], (pw or "").strip()):
            return (False, None, "아이디/비밀번호 오류")

        MemberRepository.update_last_login(member["id"])
        # 최신값 반영 위해 다시 조회(선택)
        member = MemberRepository.find_by_id(member["id"])
        return (True, member, "로그인 성공")

    @staticmethod
    def find_id(name: str, email: str):
        uid = MemberRepository.find_uid_by_name_email((name or "").strip(), (email or "").strip())
        if not uid:
            return None
        # 마스킹: 앞 2~3글자만 남김
        head = uid[:2]
        return f"{head}****"
