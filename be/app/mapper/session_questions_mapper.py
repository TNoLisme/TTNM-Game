from uuid import UUID
from datetime import datetime
import json
from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
from app.domain.sessions.session_questions import SessionQuestions
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.sessions.session_questions_schema import SessionQuestionsSchema

class SessionQuestionsMapper:
    @staticmethod
    def to_domain(session_questions_model: SessionQuestionsModel) -> SessionQuestions:
        """ĐỌC TỪ DB (NVARCHAR/JSON) sang LOGIC (Dict)"""
        if not session_questions_model:
            return None
            
        question = QuestionsMapper.to_domain(session_questions_model.question)
        
        user_answer_dict = {}
        try:
            # Xử lý decode nếu DB trả về bytes
            ua_str = session_questions_model.user_answer
            if isinstance(ua_str, bytes):
                ua_str = ua_str.decode('utf-8')
            user_answer_dict = json.loads(ua_str)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
            pass

        correct_answer_dict = {}
        try:
            # Xử lý decode nếu DB trả về bytes
            ca_str = session_questions_model.correct_answer
            if isinstance(ca_str, bytes):
                ca_str = ca_str.decode('utf-8')
            correct_answer_dict = json.loads(ca_str)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
            pass

        return SessionQuestions(
            id=session_questions_model.id,
            session_id=session_questions_model.session_id,
            question_id=question.question_id if question else session_questions_model.question_id,
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
        """LƯU VÀO DB (NVARCHAR/JSON) từ LOGIC (Dict)"""
        if not session_questions_domain:
            return None
            
        q_id = None
        if session_questions_domain.question_id:
            q_id = session_questions_domain.question_id
        elif hasattr(session_questions_domain, 'question_id'):
            q_id = session_questions_domain.question_id

        return SessionQuestionsModel(
            id=session_questions_domain.id,
            session_id=session_questions_domain.session_id,
            question_id=q_id,
            
            # SỬA LỖI FONT: ensure_ascii=False để lưu tiếng Việt có dấu
            user_answer=json.dumps(session_questions_domain.user_answer, ensure_ascii=False),
            correct_answer=json.dumps(session_questions_domain.correct_answer, ensure_ascii=False),
            
            is_correct=session_questions_domain.is_correct,
            response_time_ms=session_questions_domain.response_time_ms,
            check_hint=session_questions_domain.check_hint,
            cv_confidence=session_questions_domain.cv_confidence,
            timestamp=session_questions_domain.timestamp
        )

    @staticmethod
    def to_response(session_questions_model: SessionQuestionsModel) -> SessionQuestionsSchema.SessionQuestionsResponse:
        """ĐỌC TỪ DB (NVARCHAR/JSON) sang JSON (cho FE)"""
        if not session_questions_model:
            return None
            
        user_answer_dict = {}
        try:
            ua_str = session_questions_model.user_answer
            if isinstance(ua_str, bytes):
                ua_str = ua_str.decode('utf-8')
            user_answer_dict = json.loads(ua_str)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
            pass

        correct_answer_dict = {}
        try:
            ca_str = session_questions_model.correct_answer
            if isinstance(ca_str, bytes):
                ca_str = ca_str.decode('utf-8')
            correct_answer_dict = json.loads(ca_str)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
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