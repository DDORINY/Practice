from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Dict, Any

from werkzeug.utils import secure_filename

from lms.common.db import db_session
from lms.repository.file_repository import FileRepository
from lms.repository.ocr_job_repository import OCRJobRepository
from lms.repository.food_repository import FoodRepository
from lms.repository.inbody_repository import InbodyRepository
from lms.service.ocr_service import OCRService
from lms.service.parser_service import ParserService

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

class UploadService:

    @staticmethod
    def _save_file(file_storage) -> str:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = secure_filename(file_storage.filename)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_name = f"{ts}_{filename}"
        path = os.path.join(UPLOAD_DIR, saved_name)
        file_storage.save(path)
        return path

    @staticmethod
    def upload_nutrition_label(user_id: int, file_storage, product_name: str) -> Dict[str, Any]:
        with db_session() as conn:
            path = UploadService._save_file(file_storage)
            file_id = FileRepository.create(
                conn, user_id, "nutrition_label_image", path,
                file_storage.filename, file_storage.mimetype, None
            )
            job_id = OCRJobRepository.create_nutrition_job(conn, user_id, file_id)

            # OCR
            raw_text, conf = OCRService.extract_text(path)
            fields = ParserService.parse_nutrition_label(raw_text)

            OCRJobRepository.update_nutrition_done(
                conn, job_id, raw_text, conf,
                json.dumps(fields, ensure_ascii=False)
            )

            # 제품 생성(검수 전 임시 생성)
            product_id = FoodRepository.create_from_ocr(conn, product_name or "OCR 제품", fields, job_id, raw_text)

            return {"file_id": file_id, "job_id": job_id, "product_id": product_id, "fields": fields, "raw_text": raw_text}

    @staticmethod
    def upload_inbody(user_id: int, file_storage, measured_at: str) -> Dict[str, Any]:
        with db_session() as conn:
            path = UploadService._save_file(file_storage)
            file_id = FileRepository.create(
                conn, user_id, "inbody_image", path,
                file_storage.filename, file_storage.mimetype, None
            )
            job_id = OCRJobRepository.create_inbody_job(conn, user_id, file_id)

            raw_text, conf = OCRService.extract_text(path)
            fields = ParserService.parse_inbody(raw_text)

            OCRJobRepository.update_inbody_done(
                conn, job_id, raw_text, conf,
                json.dumps(fields, ensure_ascii=False)
            )

            report_id = InbodyRepository.create_report(conn, user_id, measured_at, fields, file_id, raw_text, conf)
            return {"file_id": file_id, "job_id": job_id, "report_id": report_id, "fields": fields, "raw_text": raw_text}