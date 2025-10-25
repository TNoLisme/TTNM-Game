from uuid import UUID
from datetime import datetime
from models.sessions.session import Session as SessionModel
from domain.sessions.session import Session, SessionStateEnum
from mapper.questions_mapper import QuestionsMapper
from schemas.sessions.session_schema import SessionSchema  # Giả định schema
from typing import List

class SessionsMapper:
    @staticmethod
    def to_domain(session_model: SessionModel) -> Session:
        """Chuyển đổi từ model sang domain entity."""
        if not session_model:
            return None
        questions = [QuestionsMapper.to_domain(q) for q in session_model.session_questions]
        return Session(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=SessionStateEnum(session_model.state),
            score=session_model.score,
            emotion_errors=session_model.emotion_errors,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=session_model.ratio,
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
            emotion_errors=session_domain.emotion_errors,
            max_errors=session_domain.max_errors,
            level_threshold=session_domain.level_threshold,
            ratio=session_domain.ratio,
            time_limit=session_domain.time_limit,
            question_ids=[q.question_id for q in session_domain.questions]  # Lưu mảng question_ids
        )

    @staticmethod
    def to_response(session_model: SessionModel) -> SessionSchema.SessionResponse:
        """Chuyển đổi từ model sang response schema."""
        if not session_model:
            return None
        return SessionSchema.SessionResponse(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=session_model.state,
            score=session_model.score,
            emotion_errors=session_model.emotion_errors,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=session_model.ratio,
            time_limit=session_model.time_limit,
            questions=[QuestionsMapper.to_response(q) for q in session_model.session_questions],
            end_time=session_model.end_time
        )