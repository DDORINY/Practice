from lms.common.db import get_connection

class AdminService:
    @staticmethod
    def get_dashboard_stats():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) cnt FROM members")
                total = cur.fetchone()["cnt"]
                cur.execute("SELECT COUNT(*) cnt FROM members WHERE active=1")
                active = cur.fetchone()["cnt"]
                cur.execute("SELECT COUNT(*) cnt FROM members WHERE active=0")
                inactive = cur.fetchone()["cnt"]
                cur.execute("SELECT COUNT(*) cnt FROM members WHERE DATE(created_at)=CURDATE()")
                today_join = cur.fetchone()["cnt"]
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "today_join": today_join,
                "today_inquiry": 0,  # 문의 테이블 붙이면 교체
            }
        finally:
            conn.close()
