from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

from lms.common.db import db_session
from lms.repository.chat_repository import ChatRepository
from lms.service.ai_service import AIService
from lms.service.calendar_service import CalendarService


class ChatService:

    @staticmethod
    def _get_or_create_session(conn, user_id: int) -> int:
        latest = ChatRepository.get_latest_session(conn, user_id)
        if latest:
            return latest["id"]
        return ChatRepository.create_session(conn, user_id)

    @staticmethod
    def _schedule_from_actions(conn, user_id: int, actions: List[Dict[str, Any]]) -> int:

        # ✅ 오늘 이미 AI 일정 있으면 생성 안함
        if CalendarService.exists_ai_event_today(conn, user_id):
            return 0

        now = datetime.now()
        created = 0

        for a in actions:
            if a.get("type") not in ("workout", "habit"):
                continue

            title = a.get("title") or "AI 추천"
            detail = a.get("detail") or ""
            memo = f"{title} - {detail}".strip(" -")

            start = now + timedelta(hours=2)
            end = start + timedelta(minutes=30)

            CalendarService.create_appointment_with_conn(
                conn,
                user_id,
                start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"),
                memo=memo,
                title=f"AI: {title}"
            )

            created += 1
            break  # 최대 1개만

        return created

    @staticmethod
    def _build_summary(user_message: str, ai_response: Dict[str, Any]) -> str:
        analysis = ai_response.get("analysis", "")
        return f"최근 상담 요약:\n사용자: {user_message}\nAI: {analysis[:200]}"

    @staticmethod
    def chat(user_id: int, message: str):

        with db_session() as conn:

            # ✅ 세션 유지
            session_id = ChatService._get_or_create_session(conn, user_id)

            ChatRepository.add_message(conn, session_id, "user", message)

            ai_response = AIService.ask(user_id, message)

            ChatRepository.add_message(
                conn,
                session_id,
                "assistant",
                json.dumps(ai_response, ensure_ascii=False),
                model="gpt-4o-mini"
            )

            # ✅ 자동 일정 생성
            actions = ai_response.get("action_plan") or []
            created = 0
            if isinstance(actions, list) and actions:
                created = ChatService._schedule_from_actions(conn, user_id, actions)

            # ✅ 세션 요약 자동 갱신
            summary = ChatService._build_summary(message, ai_response)
            ChatRepository.update_summary(conn, session_id, summary)

            ai_response["calendar_created"] = created

            return ai_response