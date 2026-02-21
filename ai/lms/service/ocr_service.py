from __future__ import annotations
import os
from typing import Tuple, Optional

from PIL import Image

class OCRService:
    """
    - pytesseract가 설치되어 있으면 OCR 수행
    - 없으면 RuntimeError 발생 (UI에서 안내)
    """

    @staticmethod
    def extract_text(image_path: str) -> Tuple[str, Optional[float]]:
        try:
            import pytesseract  # type: ignore
        except Exception:
            raise RuntimeError("pytesseract가 설치되지 않았습니다. (pip install pytesseract)")

        # (선택) Windows Tesseract 설치 경로가 필요하면 여기서 설정
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        img = Image.open(image_path)

        # 한국어+영어 OCR: Tesseract 언어팩(ko) 설치되어 있으면 "kor+eng"
        # 없으면 eng만 동작할 수 있음
        try:
            text = pytesseract.image_to_string(img, lang="kor+eng")
        except Exception:
            text = pytesseract.image_to_string(img)

        # confidence는 pytesseract 기본 API로는 계산이 번거로워서 None 처리
        return text, None