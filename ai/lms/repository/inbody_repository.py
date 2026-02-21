from __future__ import annotations
from typing import Any, Dict, Optional
from pymysql.connections import Connection
from lms.repository.base_repository import BaseRepository

class InbodyRepository(BaseRepository):

    @staticmethod
    def create_report(conn: Connection, user_id: int, measured_at: str, fields: Dict[str, Any],
                      file_id: Optional[int], raw_text: str, confidence=None) -> int:
        sql = """
        INSERT INTO inbody_reports
          (user_id, measured_at, weight_kg, smm_kg, bfm_kg, pbf_pct, bmr_kcal, visceral_level,
           file_id, raw_text, extracted_json, confidence)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s)
        """
        import json
        return InbodyRepository.insert(conn, sql, (
            user_id, measured_at,
            fields.get("weight_kg"),
            fields.get("smm_kg"),
            fields.get("bfm_kg"),
            fields.get("pbf_pct"),
            fields.get("bmr_kcal"),
            fields.get("visceral_level"),
            file_id,
            raw_text,
            json.dumps(fields, ensure_ascii=False),
            confidence
        ))