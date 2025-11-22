# app/mapper/session_questions_mapper.py
from uuid import UUID
from datetime import datetime
import json  # <-- THÊM IMPORT
from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
from app.domain.sessions.session_questions import SessionQuestions
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.sessions.session_questions_schema import SessionQuestionsSchema

class SessionQuestionsMapper:
    @staticmethod
    def to_domain(session_questions_model: SessionQuestionsModel) -> SessionQuestions:
        """ĐỌC TỪ DB (NVARCHAR) sang LOGIC (Dict)"""
        if not session_questions_model:
            return None
            
        question = QuestionsMapper.to_domain(session_questions_model.question)
        
        user_answer_dict = {}
        try:
            user_answer_dict = json.loads(session_questions_model.user_answer)
        except (json.JSONDecodeError, TypeError):
            pass

        correct_answer_dict = {}
        try:
            correct_answer_dict = json.loads(session_questions_model.correct_answer)
        except (json.JSONDecodeError, TypeError):
            pass

        return SessionQuestions(
            id=session_questions_model.id,
            session_id=session_questions_model.session_id,
            question_id=question.question_id,
            user_answer=user_answer_dict,
            correct_answer=correct_answer_dict,
            is_correct=session_questions_model.is_correct,
            response_time_ms=session_questions_model.response_time_ms,
            check_hint=session_questions_model.check_hint,
            cv_confidence=session_questions_model.cv_confidence,
            timestamp=session_questions_model.timestamp
        )

    @staticmethod
    def to_model(session_questions_domain: SessionQuestions) -> SessionQuestionsModel:
        """LƯU VÀO DB (NVARCHAR) từ LOGIC (Dict)"""
        if not session_questions_domain:
            return None
            
        # === SỬA LỖI Ở ĐÂY ===
        
        q_id = None
        if session_questions_domain.question_id:
            q_id = session_questions_domain.question_id
        elif hasattr(session_questions_domain, 'question_id'):
            q_id = session_questions_domain.question_id

        return SessionQuestionsModel(
            id=session_questions_domain.id,
            session_id=session_questions_domain.session_id,
            question_id=q_id,
            
            # Dùng json.dumps() để chuyển Dict thành CHUỖI JSON
            user_answer=json.dumps(session_questions_domain.user_answer),
            correct_answer=json.dumps(session_questions_domain.correct_answer),
            # === HẾT SỬA ===
            
            is_correct=session_questions_domain.is_correct,
            response_time_ms=session_questions_domain.response_time_ms,
            check_hint=session_questions_domain.check_hint,
            cv_confidence=session_questions_domain.cv_confidence,
            timestamp=session_questions_domain.timestamp
        )

    @staticmethod
    def to_response(session_questions_model: SessionQuestionsModel) -> SessionQuestionsSchema.SessionQuestionsResponse:
        """ĐỌC TỪ DB (NVARCHAR) sang JSON (cho FE)"""
        if not session_questions_model:
            return None
            
        user_answer_dict = {}
        try:
            user_answer_dict = json.loads(session_questions_model.user_answer)
        except (json.JSONDecodeError, TypeError):
            pass

        correct_answer_dict = {}
        try:
            correct_answer_dict = json.loads(session_questions_model.correct_answer)
        except (json.JSONDecodeError, TypeError):
            pass
            
        return SessionQuestionsSchema.SessionQuestionsResponse(
            id=session_questions_model.id,
            session_id=session_questions_model.session_id,
            question=QuestionsMapper.to_response(session_questions_model.question),
            user_answer=user_answer_dict,
            correct_answer=correct_answer_dict,
            is_correct=session_questions_model.is_correct,
            response_time_ms=session_questions_model.response_time_ms,
            check_hint=session_questions_model.check_hint,
            cv_confidence=session_questions_model.cv_confidence,
            timestamp=session_questions_model.timestamp
        )