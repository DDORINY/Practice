from __future__ import annotations
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from lms.common.db import db_session
from lms.repository.prediction_repository import PredictionRepository
from lms.repository.profile_repository import ProfileRepository

def _linear_regression_slope(xs: List[float], ys: List[float]) -> float:
    # slope = cov(x,y)/var(x)
    n = len(xs)
    if n < 2:
        return 0.0
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    return num / den if den != 0 else 0.0

class PredictionService:
    """
    다음 7일 체중 예측(설명 가능한 하이브리드):
    - 최근 체중의 추세(일일 기울기) 기반 예측
    - 최근 7일 칼로리 밸런스(섭취-소모-TDEE추정)로 보정
    """

    @staticmethod
    def predict_next_7_days(user_id: int) -> Dict[str, Any]:
        with db_session() as conn:
            weight_rows = PredictionRepository.get_weight_series(conn, user_id, 21)
            balance_rows = PredictionRepository.get_daily_balance(conn, user_id, 7)
            targets = ProfileRepository.get_targets(conn, user_id) or {}

        # 체중 시계열 준비
        series = [(r["d"], r["w"]) for r in weight_rows if r.get("w") is not None]
        if len(series) < 5:
            return {
                "ok": False,
                "message": "체중 데이터가 부족합니다(최소 5일 이상 권장).",
                "predictions": []
            }

        # x: 0..n-1 (날짜 인덱스), y: weight
        ys = [float(w) for _, w in series]
        xs = [float(i) for i in range(len(ys))]
        slope_per_day = _linear_regression_slope(xs, ys)  # kg/day

        last_date = series[-1][0]
        last_weight = ys[-1]

        # TDEE 추정(간단): target_kcal이 있으면 그것을 '유지' 근사치로 사용
        # (정교하게 하려면 BMR+activity로 계산하지만, MVP에선 이게 현실적)
        tdee = targets.get("target_kcal") or 1800

        # 최근 7일 평균 에너지 밸런스(섭취 - 소모 - tdee)
        balances = []
        for r in balance_rows:
            intake = int(r.get("intake_kcal") or 0)
            burn = int(r.get("burn_kcal") or 0)
            balances.append(intake - burn - int(tdee))

        avg_balance = sum(balances) / len(balances) if balances else 0.0

        # 7700kcal ≈ 체지방 1kg 가정 (단순 근사)
        kcal_to_kg = 1.0 / 7700.0
        balance_slope = avg_balance * kcal_to_kg  # kg/day 보정

        # 최종 slope: 체중 추세 + 밸런스 보정(너무 튀지 않게 가중치)
        final_slope = (slope_per_day * 0.7) + (balance_slope * 0.3)

        preds = []
        for day in range(1, 8):
            d = last_date + timedelta(days=day)
            pred_w = last_weight + final_slope * day
            preds.append({"date": d.isoformat(), "pred_weight_kg": round(pred_w, 2)})

        return {
            "ok": True,
            "last_weight_kg": round(last_weight, 2),
            "trend_slope_kg_per_day": round(slope_per_day, 4),
            "avg_balance_kcal_per_day": round(avg_balance, 1),
            "final_slope_kg_per_day": round(final_slope, 4),
            "predictions": preds,
            "assumptions": {
                "tdee_kcal_used": int(tdee),
                "kcal_per_kg": 7700
            }
        }