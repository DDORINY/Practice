from __future__ import annotations
import os
import json
from typing import Dict, Any

from openai import OpenAI
from lms.common.db import db_session
from lms.repository.base_repository import BaseRepository
from lms.service.recommendation_service import RecommendationService
from lms.repository.weight_repository import WeightRepository

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AIService(BaseRepository):

    @staticmethod
    def _get_recent_summary(conn, user_id: int) -> Dict[str, Any]:
        """
        최근 7일 평균 섭취/운동 요약
        """
        sql = """
        SELECT
          AVG(total_kcal) AS avg_kcal,
          AVG(total_protein_g) AS avg_protein,
          AVG(total_sodium_mg) AS avg_sodium
        FROM daily_nutrition_summary
        WHERE user_id=%s
          AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        nutri = AIService.fetchone(conn, sql, (user_id,)) or {}

        sql2 = """
        SELECT
          AVG(total_kcal_burn) AS avg_burn
        FROM daily_activity_summary
        WHERE user_id=%s
          AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        act = AIService.fetchone(conn, sql2, (user_id,)) or {}

        return {
            "avg_kcal": nutri.get("avg_kcal") or 0,
            "avg_protein": nutri.get("avg_protein") or 0,
            "avg_sodium": nutri.get("avg_sodium") or 0,
            "avg_burn": act.get("avg_burn") or 0,
        }

    @staticmethod
    def ask(user_id: int, user_message: str):
        with db_session() as conn:

            # 최근 7일 평균
            summary = AIService._get_recent_summary(conn, user_id)

            # 체중 추세
            trend = AIService._get_weight_trend(conn, user_id)

            # 오늘 추천 데이터 (이미 생성되어 있다면)
            today_data = RecommendationService.generate_today(user_id)

            system_prompt = f"""
You are a professional diet coach.

User context:
- 7day avg kcal: {summary['avg_kcal']}
- 7day avg protein: {summary['avg_protein']}
- 7day avg sodium: {summary['avg_sodium']}
- 7day avg burn: {summary['avg_burn']}

- Today remaining kcal: {today_data['recommendation']['remaining_kcal']}
- Today protein gap: {today_data['recommendation']['protein_gap_g']}

- Weight trend: {trend['trend_msg']}
- Plateau: {trend['plateau']}

Respond in JSON format only:

{{
  "analysis": "...",
  "risk_level": "low | moderate | high",
  "action_plan": [
    {{"type":"meal","title":"...","detail":"..."}},
    {{"type":"workout","title":"...","detail":"..."}},
    {{"type":"habit","title":"...","detail":"..."}}
  ]
}}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6
            )

            content = response.choices[0].message.content

            try:
                parsed = json.loads(content)
            except Exception:
                parsed = {
                    "analysis": content,
                    "risk_level": "unknown",
                    "action_plan": []
                }

            return parsed

    @staticmethod
    def _get_weight_trend(conn, user_id: int):
        weights = WeightRepository.list_last_days(conn, user_id, 14)

        if (
                len(weights) >= 8
                and weights[0].get("w") is not None
                and weights[-1].get("w") is not None
        ):
            first = float(weights[0]["w"])
            last = float(weights[-1]["w"])
            diff = last - first

            if abs(diff) < 0.3:
                return {
                    "plateau": True,
                    "trend_msg": "최근 2주 체중 변화 거의 없음 (정체기 가능성)"
                }
            else:
                direction = "감소" if diff < 0 else "증가"
                return {
                    "plateau": False,
                    "trend_msg": f"최근 2주 체중 {abs(diff):.1f}kg {direction}"
                }

        return {
            "plateau": False,
            "trend_msg": "체중 데이터 부족"
        }