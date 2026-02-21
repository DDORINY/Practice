from __future__ import annotations
import json
from typing import Any, Dict, Optional, Tuple

from lms.common.db import db_session
from lms.repository.profile_repository import ProfileRepository
from lms.repository.daily_query_repository import DailyQueryRepository
from lms.repository.recommendation_repository import RecommendationRepository
from lms.repository.weight_repository import WeightRepository

def _clamp_int(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, x))

class RecommendationService:
    """
    규칙 기반 추천 v1:
    - remaining_kcal = target_kcal - today_kcal (운동 소모는 별도 표기만; 1차에선 섭취 기준)
    - protein_gap = target_protein - today_protein
    - sodium_warning: 목표 또는 2000mg 기준 초과 시
    - coach_message/action_plan_json 생성
    """

    @staticmethod
    def generate_today(user_id: int) -> Dict[str, Any]:
        with db_session() as conn:
            targets = ProfileRepository.get_targets(conn, user_id) or {}
            nutri = DailyQueryRepository.get_today_nutrition(conn, user_id)
            act = DailyQueryRepository.get_today_activity(conn, user_id)

            weights = WeightRepository.list_last_days(conn, user_id, 14)
            plateau = False
            trend_msg = ""

            # ✅ w가 NULL(=None)인 경우 float(None)에서 터지는 걸 방지
            if (
                    len(weights) >= 8
                    and weights[0].get("w") is not None
                    and weights[-1].get("w") is not None
            ):
                first = float(weights[0]["w"])
                last = float(weights[-1]["w"])
                diff = last - first  # (+)면 증가, (-)면 감소

                if abs(diff) < 0.3:
                    plateau = True
                    trend_msg = "최근 2주 체중 변화가 거의 없어 정체기 가능성이 있어요."
                else:
                    direction = "감소" if diff < 0 else "증가"
                    trend_msg = f"최근 2주 체중이 약 {abs(diff):.1f}kg {direction}했어요."
            else:
                trend_msg = "체중 데이터가 더 쌓이면 추세 분석이 정확해져요."

            target_kcal = targets.get("target_kcal") or 1800
            target_protein = targets.get("target_protein_g") or 120
            target_sodium = targets.get("target_sodium_mg") or 2000

            today_kcal = int(nutri["total_kcal"] or 0)
            today_protein = float(nutri["total_protein_g"] or 0)
            today_sodium = int(nutri["total_sodium_mg"] or 0)
            kcal_burn = int(act["total_kcal_burn"] or 0)

            remaining_kcal = target_kcal - today_kcal
            protein_gap = target_protein - today_protein

            sodium_warning = 1 if today_sodium > target_sodium else 0

            coach_message, actions = RecommendationService._build_message_and_actions(
                remaining_kcal=remaining_kcal,
                protein_gap=protein_gap,
                sodium_warning=sodium_warning,
                kcal_burn=kcal_burn,
                plateau=plateau,
                trend_msg=trend_msg
            )

            # UI용: 음수 remaining은 -300 이하로 과도하게 내려가지 않게(표시 안정)
            remaining_kcal_display = _clamp_int(remaining_kcal, -2000, 5000)

            RecommendationRepository.upsert_today(
                conn,
                user_id=user_id,
                date_str="{}".format(__import__("datetime").date.today().isoformat()),
                remaining_kcal=remaining_kcal_display,
                protein_gap_g=round(protein_gap, 2),
                carb_limit_g=None,
                fat_limit_g=None,
                sodium_warning=sodium_warning,
                coach_message=coach_message,
                action_plan_json=json.dumps(actions, ensure_ascii=False),
                model=None,
                prompt_version="rule-v1"
            )

            return {
                "targets": {"kcal": target_kcal, "protein_g": target_protein, "sodium_mg": target_sodium},
                "today": {"kcal": today_kcal, "protein_g": today_protein, "sodium_mg": today_sodium, "burn_kcal": kcal_burn},
                "recommendation": {
                    "remaining_kcal": remaining_kcal_display,
                    "protein_gap_g": round(protein_gap, 2),
                    "sodium_warning": sodium_warning,
                    "coach_message": coach_message,
                    "actions": actions,
                }
            }

    @staticmethod
    def _build_message_and_actions(
            remaining_kcal: int,
            protein_gap: float,
            sodium_warning: int,
            kcal_burn: int,
            plateau: bool,
            trend_msg: str
    ):
        actions = []

        # 칼로리 상태
        if remaining_kcal >= 300:
            kcal_msg = f"오늘 목표까지 약 {remaining_kcal}kcal 남았어요."
            actions.append({
                "type": "meal",
                "title": "남은 칼로리 내에서 식사",
                "detail": "저녁은 단백질+채소 위주로 구성",
                "reason": "목표 칼로리 내 마감"
            })
        elif 0 <= remaining_kcal < 300:
            kcal_msg = f"오늘은 목표 칼로리에 거의 도달했어요(잔여 {remaining_kcal}kcal)."
            actions.append({
                "type": "meal",
                "title": "가벼운 마무리",
                "detail": "간식은 과일/요거트 등 소량",
                "reason": "초과 방지"
            })
        else:
            over = abs(remaining_kcal)
            kcal_msg = f"오늘은 목표보다 약 {over}kcal 초과했어요."
            actions.append({
                "type": "workout",
                "title": "가벼운 추가 활동",
                "detail": "빠른 걷기 30분 또는 스트레칭 15분",
                "reason": "칼로리 밸런스 보정"
            })

        # 단백질 상태
        if protein_gap >= 15:
            pro_msg = f"단백질이 약 {int(protein_gap)}g 부족해요."
            actions.append({
                "type": "meal",
                "title": "단백질 보충",
                "detail": "닭가슴살 100g / 계란 2개 / 그릭요거트 1컵 중 택1",
                "reason": "근손실 방지 및 포만감"
            })
        elif 0 < protein_gap < 15:
            pro_msg = f"단백질이 조금 부족해요(+{int(protein_gap)}g)."
            actions.append({
                "type": "meal",
                "title": "소량 단백질 추가",
                "detail": "두부/우유/요거트 등으로 보충",
                "reason": "목표치 근접"
            })
        else:
            pro_msg = "단백질은 오늘 목표를 잘 채웠어요."
            actions.append({
                "type": "habit",
                "title": "유지하기",
                "detail": "내일도 단백질을 끼니마다 분배",
                "reason": "일관성이 핵심"
            })

        # 나트륨 경고
        if sodium_warning:
            na_msg = "나트륨 섭취가 높은 편이에요. 내일은 국물/가공식품을 줄여보세요."
            actions.append({
                "type": "meal",
                "title": "나트륨 낮추기",
                "detail": "국물은 반만, 가공식품/소스 줄이기",
                "reason": "붓기/컨디션 관리"
            })
        else:
            na_msg = "나트륨은 큰 문제 없어요."

        # 운동 소모는 참고 정보로 가볍게
        burn_msg = f"오늘 운동 소모(기록 기준) {kcal_burn}kcal." if kcal_burn else "오늘 운동 기록이 아직 없어요."

        coach_message = f"{kcal_msg} {pro_msg} {na_msg} {burn_msg} {trend_msg}"

        if plateau:
            actions.append({
                "type": "habit",
                "title": "정체기 대응",
                "detail": "2~3일만 간식/음료 점검 + 걷기 20분 추가 + 단백질 유지로 실험",
                "reason": "정체기 원인 확인"
            })

        return coach_message, actions