from __future__ import annotations
import re
from typing import Dict, Any, Optional

class ParserService:

    @staticmethod
    def parse_nutrition_label(text: str) -> Dict[str, Any]:
        """
        영양성분표 텍스트에서 대표 항목 추출:
        kcal, carbs_g, protein_g, fat_g, sugar_g, sodium_mg, serving_size_g(가능하면)
        """
        t = text.replace(",", " ")
        def find_float(patterns) -> Optional[float]:
            for p in patterns:
                m = re.search(p, t, re.IGNORECASE)
                if m:
                    return float(m.group(1))
            return None

        def find_int(patterns) -> Optional[int]:
            v = find_float(patterns)
            return int(v) if v is not None else None

        # 1회 제공량(가능하면)
        serving = find_float([
            r"1회\s*제공량\s*([0-9]+(?:\.[0-9]+)?)\s*g",
            r"총\s*내용량.*?([0-9]+(?:\.[0-9]+)?)\s*g",
            r"serving\s*size\s*([0-9]+(?:\.[0-9]+)?)\s*g",
        ])

        kcal = find_int([
            r"열량\s*([0-9]+(?:\.[0-9]+)?)\s*kcal",
            r"calories\s*([0-9]+(?:\.[0-9]+)?)",
        ])

        carbs = find_float([
            r"탄수화물\s*([0-9]+(?:\.[0-9]+)?)\s*g",
            r"carbohydrate\s*([0-9]+(?:\.[0-9]+)?)\s*g",
        ])

        protein = find_float([
            r"단백질\s*([0-9]+(?:\.[0-9]+)?)\s*g",
            r"protein\s*([0-9]+(?:\.[0-9]+)?)\s*g",
        ])

        fat = find_float([
            r"지방\s*([0-9]+(?:\.[0-9]+)?)\s*g",
            r"fat\s*([0-9]+(?:\.[0-9]+)?)\s*g",
        ])

        sugar = find_float([
            r"당류\s*([0-9]+(?:\.[0-9]+)?)\s*g",
            r"sugars?\s*([0-9]+(?:\.[0-9]+)?)\s*g",
        ])

        sodium = find_int([
            r"나트륨\s*([0-9]+(?:\.[0-9]+)?)\s*mg",
            r"sodium\s*([0-9]+(?:\.[0-9]+)?)\s*mg",
        ])

        return {
            "serving_size_g": serving,
            "kcal": kcal,
            "carbs_g": carbs,
            "protein_g": protein,
            "fat_g": fat,
            "sugar_g": sugar,
            "sodium_mg": sodium,
        }

    @staticmethod
    def parse_inbody(text: str) -> Dict[str, Any]:
        """
        인바디 원문에서 대표 항목 추출(가능한 것만):
        weight_kg, smm_kg, bfm_kg, pbf_pct, bmr_kcal, visceral_level
        """
        t = text.replace(",", " ")

        def find_float(patterns) -> Optional[float]:
            for p in patterns:
                m = re.search(p, t, re.IGNORECASE)
                if m:
                    return float(m.group(1))
            return None

        def find_int(patterns) -> Optional[int]:
            v = find_float(patterns)
            return int(v) if v is not None else None

        weight = find_float([
            r"체중\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
            r"Weight\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
        ])

        smm = find_float([
            r"골격근량\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
            r"SMM\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
        ])

        bfm = find_float([
            r"체지방량\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
            r"Body\s*Fat\s*Mass\s*([0-9]+(?:\.[0-9]+)?)\s*kg",
        ])

        pbf = find_float([
            r"체지방률\s*([0-9]+(?:\.[0-9]+)?)\s*%",
            r"PBF\s*([0-9]+(?:\.[0-9]+)?)\s*%",
        ])

        bmr = find_int([
            r"기초대사량\s*([0-9]+(?:\.[0-9]+)?)\s*kcal",
            r"BMR\s*([0-9]+(?:\.[0-9]+)?)",
        ])

        visceral = find_float([
            r"내장지방.*?([0-9]+(?:\.[0-9]+)?)",
            r"Visceral.*?([0-9]+(?:\.[0-9]+)?)",
        ])

        return {
            "weight_kg": weight,
            "smm_kg": smm,
            "bfm_kg": bfm,
            "pbf_pct": pbf,
            "bmr_kcal": bmr,
            "visceral_level": visceral
        }