import re
from datetime import date

# 유틸(마스킹/ 주민번호-> 생일 추척

def mask_phone(phone: str) -> str:
    # 연락처가 없는 경우
    if not phone:
        return ""

    #연락처 글자 수 정하기&마스킹 설정
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10:
        return phone
    # 01012345678 -> 010-1234-****
    return f"{digits[:3]}-{digits[3:8]}-****"

    #이메일 마스킹
def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return email or ""
    name, domain = email.split("@", 1)
    head = name[:2]
    return f"{head}***@{domain}"

def mask_address(addr: str) -> str:
    if not addr:
        return ""
    # 마스킹 뒤쪽만
    if len(addr) <= 6:
        return "***"
    return addr[:6] + " ***"

def rrn_to_birthdate(rrn: str) -> date:
    """
    주민번호(000000-0000000 또는 숫자만) -> birthdate(date)
    원문 저장하지 않고 생일만 추출.
    """
    if not rrn:
        raise ValueError("rrn required")

    v = re.sub(r"\D", "", rrn)
    if len(v) != 13:
        raise ValueError("rrn format")

    yy = int(v[0:2])
    mm = int(v[2:4])
    dd = int(v[4:6])
    code = v[6]  # 세기 코드

    if code in ("1", "2"):
        year = 1900 + yy
    elif code in ("3", "4"):
        year = 2000 + yy
    else:
        # 시험/과제용 안전 처리
        raise ValueError("rrn century code")

    return date(year, mm, dd)