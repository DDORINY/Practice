from __future__ import annotations
from typing import Optional, Dict, Any
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class OCRJobRepository(BaseRepository):

    @staticmethod
    def create_inbody_job(conn: Connection, user_id: int, file_id: int, engine: str="tesseract") -> int:
        sql = """
        INSERT INTO inbody_ocr_jobs (user_id, file_id, status, ocr_engine)
        VALUES (%s, %s, 'queued', %s)
        """
        return OCRJobRepository.insert(conn, sql, (user_id, file_id, engine))

    @staticmethod
    def create_nutrition_job(conn: Connection, user_id: int, file_id: int, engine: str="tesseract") -> int:
        sql = """
        INSERT INTO nutrition_label_ocr_jobs (user_id, file_id, status, ocr_engine)
        VALUES (%s, %s, 'queued', %s)
        """
        return OCRJobRepository.insert(conn, sql, (user_id, file_id, engine))

    @staticmethod
    def update_inbody_done(conn: Connection, job_id: int, raw_text: str, confidence, extracted_json, status="done"):
        sql = """
        UPDATE inbody_ocr_jobs
        SET status=%s, raw_text=%s, confidence=%s, extracted_json=%s, updated_at=NOW()
        WHERE id=%s
        """
        return OCRJobRepository.execute(conn, sql, (status, raw_text, confidence, extracted_json, job_id))

    @staticmethod
    def update_nutrition_done(conn: Connection, job_id: int, raw_text: str, confidence, extracted_json, status="done"):
        sql = """
        UPDATE nutrition_label_ocr_jobs
        SET status=%s, raw_text=%s, confidence=%s, extracted_json=%s, updated_at=NOW()
        WHERE id=%s
        """
        return OCRJobRepository.execute(conn, sql, (status, raw_text, confidence, extracted_json, job_id))