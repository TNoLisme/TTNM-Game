from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
from app.domain.sessions.session_questions import SessionQuestions
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.sessions.session_questions_schema import SessionQuestionsSchema  # Giả định schema
import json

class SessionQuestionsMapper:
    @staticmethod
    def to_domain(session_questions_model: SessionQuestionsModel) -> SessionQuestions:
        """Chuyển đổi từ model sang domain entity."""
        if not session_questions_model:
            return None
        question = QuestionsMapper.to_domain(session_questions_model.question)
        try:
            user_answer = json.loads(session_questions_model.user_answer) if session_questions_model.user_answer else {}
        except (TypeError, json.JSONDecodeError):
            user_answer = session_questions_model.user_answer or {}
        try:
            correct_answer = json.loads(session_questions_model.correct_answer) if session_questions_model.correct_answer else {}
        except (TypeError, json.JSONDecodeError):
            correct_answer = session_questions_model.correct_answer or {}

        return SessionQuestions(
            id=session_questions_model.id,
            session_id=session_questions_model.session_id,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=session_questions_model.is_correct,
            response_time_ms=session_questions_model.response_time_ms,
            check_hint=session_questions_model.check_hint,
            cv_confidence=session_questions_model.cv_confidence,
            timestamp=session_questions_model.timestamp
        )

    @staticmethod
    def to_model(session_questions_domain: SessionQuestions) -> SessionQuestionsModel:
        """Chuyển đổi từ domain entity sang model."""
        if not session_questions_domain:
            return None
        return SessionQuestionsModel(
            id=session_questions_domain.id,
            session_id=session_questions_domain.session_id,
            question_id=session_questions_domain.question.question_id,
            user_answer=json.dumps(session_questions_domain.user_answer or {}),
            correct_answer=json.dumps(session_questions_domain.correct_answer or {}),
            is_correct=session_questions_domain.is_correct,
            response_time_ms=session_questions_domain.response_time_ms,
            check_hint=session_questions_domain.check_hint,
            cv_confidence=session_questions_domain.cv_confidence,
            timestamp=session_questions_domain.timestamp
        )

    @staticmethod
    def to_response(session_questions_model: SessionQuestionsModel) -> SessionQuestionsSchema.SessionQuestionsResponse:
        """Chuyển đổi từ model sang response schema."""
        if not session_questions_model:
            return None
        try:
            user_answer = json.loads(session_questions_model.user_answer) if session_questions_model.user_answer else {}
        except (TypeError, json.JSONDecodeError):
            user_answer = session_questions_model.user_answer or {}
        try:
            correct_answer = json.loads(session_questions_model.correct_answer) if session_questions_model.correct_answer else {}
        except (TypeError, json.JSONDecodeError):
            correct_answer = session_questions_model.correct_answer or {}

        return SessionQuestionsSchema.SessionQuestionsResponse(
            id=session_questions_model.id,
            session_id=session_questions_model.session_id,
            question=QuestionsMapper.to_response(session_questions_model.question),
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=session_questions_model.is_correct,
            response_time_ms=session_questions_model.response_time_ms,
            check_hint=session_questions_model.check_hint,
            cv_confidence=session_questions_model.cv_confidence,
            timestamp=session_questions_model.timestamp
        )