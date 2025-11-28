import json
from app.models.sessions.session import Session as SessionModel
from app.domain.sessions.session import Session, SessionStateEnum
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.sessions.session_schema import SessionSchema  # Giả định schema
from typing import List

class SessionsMapper:
    @staticmethod
    def to_domain(session_model: SessionModel) -> Session:
        """Chuyển đổi từ model sang domain entity."""
        if not session_model:
            return None
        questions = [QuestionsMapper.to_domain(q) for q in session_model.session_questions]
        try:
            emotion_errors = json.loads(session_model.emotion_errors) if session_model.emotion_errors else {}
        except (TypeError, json.JSONDecodeError):
            emotion_errors = session_model.emotion_errors or {}

        try:
            ratio = json.loads(session_model.ratio) if session_model.ratio else []
        except (TypeError, json.JSONDecodeError):
            ratio = session_model.ratio or []

        return Session(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=session_model.state,
            score=session_model.score,
            emotion_errors=emotion_errors,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=ratio,
            time_limit=session_model.time_limit,
            questions=questions
        )

    @staticmethod
    def to_model(session_domain: Session) -> SessionModel:
        """Chuyển đổi từ domain entity sang model."""
        if not session_domain:
            return None
        return SessionModel(
            session_id=session_domain.session_id,
            user_id=session_domain.user_id,
            game_id=session_domain.game_id,
            start_time=session_domain.start_time,
            end_time=session_domain.end_time,
            state=session_domain.state.value,
            score=session_domain.score,
            emotion_errors=json.dumps(session_domain.emotion_errors or {}),
            max_errors=session_domain.max_errors,
            level_threshold=session_domain.level_threshold,
            ratio=json.dumps(session_domain.ratio or []),
            time_limit=session_domain.time_limit,
            question_ids=json.dumps([q.question_id for q in session_domain.questions])  # Lưu mảng question_ids
        )

    @staticmethod
    def to_response(session_model: SessionModel) -> SessionSchema.SessionResponse:
        """Chuyển đổi từ model sang response schema."""
        if not session_model:
            return None
        try:
            emotion_errors = json.loads(session_model.emotion_errors) if session_model.emotion_errors else {}
        except (TypeError, json.JSONDecodeError):
            emotion_errors = session_model.emotion_errors or {}

        try:
            ratio = json.loads(session_model.ratio) if session_model.ratio else []
        except (TypeError, json.JSONDecodeError):
            ratio = session_model.ratio or []

        return SessionSchema.SessionResponse(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=session_model.state,
            score=session_model.score,
            emotion_errors=emotion_errors,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=ratio,
            time_limit=session_model.time_limit,
            questions=[QuestionsMapper.to_response(q) for q in session_model.session_questions],
            end_time=session_model.end_time
        )