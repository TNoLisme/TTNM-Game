# app/mapper/sessions_mapper.py
from uuid import UUID
from datetime import datetime
import json  # <-- THÊM IMPORT
from app.models.sessions.session import Session as SessionModel
from app.domain.sessions.session import Session, SessionStateEnum
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.sessions.session_schema import SessionSchema
from typing import List

class SessionsMapper:
    @staticmethod
    def to_domain(session_model: SessionModel) -> Session:
        if not session_model:
            return None
        ratio_list = []
        try:
            ratio_list = json.loads(session_model.ratio)
        except (json.JSONDecodeError, TypeError):
            pass 

        emotion_errors_dict = {}
        try:
            emotion_errors_dict = json.loads(session_model.emotion_errors)
        except (json.JSONDecodeError, TypeError):
            pass 
        
        questions_domain = []
        if getattr(session_model, "session_questions", None):
            questions_domain = [QuestionsMapper.to_domain(sq.question) for sq in session_model.session_questions if sq.question]

        return Session(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=session_model.state,
            score=session_model.score,
            emotion_errors=emotion_errors_dict,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=ratio_list, 
            time_limit=session_model.time_limit,
            questions=questions_domain,
            level=session_model.level
        )

    @staticmethod
    def to_model(session_domain: Session) -> SessionModel:
        if not session_domain:
            return None
        # 1. Chuyển List[Question] (domain) -> List[str] (UUIDs)
        question_ids_str_list = [str(q.question_id) for q in session_domain.questions]

        return SessionModel(
            session_id=session_domain.session_id,
            user_id=session_domain.user_id,
            game_id=session_domain.game_id,
            start_time=session_domain.start_time,
            end_time=session_domain.end_time,
            state=session_domain.state.value,
            score=session_domain.score,
            emotion_errors=json.dumps(session_domain.emotion_errors),
            ratio=json.dumps(session_domain.ratio),
            question_ids=json.dumps(question_ids_str_list),   
            max_errors=session_domain.max_errors,
            level_threshold=session_domain.level_threshold,
            time_limit=session_domain.time_limit,
            level=session_domain.level
        )

    @staticmethod
    def to_response(session_model: SessionModel) -> SessionSchema.SessionResponse:
        if not session_model:
            return None
        ratio_list = []
        try:
            ratio_list = json.loads(session_model.ratio)
        except: pass
        emotion_errors_dict = {}
        try:
            emotion_errors_dict = json.loads(session_model.emotion_errors)
        except: pass
        questions_response = []
        if getattr(session_model, "session_questions", None):
             questions_response = [QuestionsMapper.to_response(sq.question) for sq in session_model.session_questions if sq.question]

        return SessionSchema.SessionResponse(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            game_id=session_model.game_id,
            start_time=session_model.start_time,
            state=session_model.state,
            score=session_model.score,
            emotion_errors=emotion_errors_dict,
            max_errors=session_model.max_errors,
            level_threshold=session_model.level_threshold,
            ratio=ratio_list,
            time_limit=session_model.time_limit,
            questions=questions_response,
            end_time=session_model.end_time,
            level=session_model.level
        )