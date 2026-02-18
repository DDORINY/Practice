from lms.common.db import get_connection

class MemberRepository:
    @staticmethod
    def find_by_uid(uid: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM members WHERE uid=%s", (uid,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(member_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM members WHERE id=%s", (member_id,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(member: dict):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO members
                (uid, pw_hash, name, phone, email, address, birthdate,
                 retention_agreed, retention_agreed_at, role, active, profile_img)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,%s)
                """
                cur.execute(sql, (
                    member["uid"], member["pw_hash"], member["name"],
                    member["phone"], member["email"], member["address"], member["birthdate"],
                    member["retention_agreed"], member.get("role","USER"),
                    1, member.get("profile_img")
                ))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def update_profile(member_id: int, name: str, phone: str, address: str, email: str, profile_img: str|None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                if profile_img:
                    sql = """UPDATE members
                             SET name=%s, phone=%s, address=%s, email=%s, profile_img=%s
                             WHERE id=%s"""
                    cur.execute(sql, (name, phone, address, email, profile_img, member_id))
                else:
                    sql = """UPDATE members
                             SET name=%s, phone=%s, address=%s, email=%s
                             WHERE id=%s"""
                    cur.execute(sql, (name, phone, address, email, member_id))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def soft_delete(member_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE members
                SET active=0,
                    deleted_at=NOW(),
                    purge_at=DATE_ADD(NOW(), INTERVAL 1 YEAR)
                WHERE id=%s
                """
                cur.execute(sql, (member_id,))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def update_last_login(member_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE members SET last_login_at=NOW() WHERE id=%s", (member_id,))
            conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()

    # 아이디 찾기: 이름+이메일
    @staticmethod
    def find_uid_by_name_email(name: str, email: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT uid FROM members WHERE name=%s AND email=%s AND active=1", (name, email))
                row = cur.fetchone()
                return row["uid"] if row else None
        finally:
            conn.close()

    # 관리자 목록/검색
    @staticmethod
    def list_members(active=None, keyword=None):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = "SELECT id, uid, name, phone, email, address, active, created_at, last_login_at FROM members WHERE 1=1"
                params = []
                if active in (0, 1):
                    sql += " AND active=%s"
                    params.append(active)
                if keyword:
                    sql += " AND (uid LIKE %s OR name LIKE %s OR email LIKE %s)"
                    like = f"%{keyword}%"
                    params.extend([like, like, like])
                sql += " ORDER BY id DESC"
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def admin_disable(member_id: int):
        """관리자: 계정 비활성(탈퇴 처리) + 1년 후 삭제 예약"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE members
                SET active=0,
                    deleted_at=NOW(),
                    purge_at=DATE_ADD(NOW(), INTERVAL 1 YEAR)
                WHERE id=%s
                """
                cur.execute(sql, (member_id,))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def admin_enable(member_id: int):
        """관리자: 비활성 계정 복구"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE members
                SET active=1,
                    deleted_at=NULL,
                    purge_at=NULL
                WHERE id=%s
                """
                cur.execute(sql, (member_id,))
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()
