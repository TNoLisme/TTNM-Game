from uuid import UUID, uuid4
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime

# Domain
from app.domain.sessions.session import Session, SessionStateEnum
from app.domain.sessions.session_questions import SessionQuestions

# Service
from app.services.analytics.child_progress_service import ChildProgressService
from app.services.games.question_service import QuestionService
from app.services.sessions.emotion_concepts_service import EmotionConceptsService
from app.services.analytics.child_progress_service import ChildProgressService
from app.services.sessions.sessions_service import SessionsService
from app.services.sessions.session_questions_service import SessionQuestionsService
from app.services.games.game_service import GameService


class GamePlayService:
    def __init__(self, db: Session):
        self.db = db
        self.games_service = GameService(db)
        self.session_service = SessionsService(db)
        self.session_questions_service = SessionQuestionsService(db)
        self.question_service = QuestionService(db)
        self.child_progress_service = ChildProgressService(db)
        self.emotion_concepts_service = EmotionConceptsService(db)

    def start_session(self, game_id: str, level: int, user_id: str) -> Dict:
        user_uuid = UUID(user_id)
        game_uuid = UUID(game_id)
        # Lấy thông tin game
        game = self.games_service.get_by_id(game_uuid)
        if not game:
            raise ValueError(f"Game not found with ID: {game_id}")

        # Lấy ratio user
        ratio = self.child_progress_service.get_ratio(user_uuid, game_uuid)

        # Lấy hoặc generate question cho session
        questions = self.question_service.get_or_generate_questions(
            user_id=user_uuid,
            game_id=game_uuid,
            level=level,
            ratio=ratio
        )
        # Format câu hỏi trước khi trả về FE
        formatted_questions = self.question_service.format_questions_for_frontend(
            questions=questions,
            game_id=game_uuid,
            level=level
        )
        # Lấy session gần nhất
        latest_session = self.session_service.get_latest_session(user_uuid, game_uuid)
        # Nếu có session cũ → dùng emotion_errors để FE hiển thị thẻ học
        emotion_errors = latest_session.emotion_errors if latest_session else {
            "sợ hãi": 0,
            "buồn bã": 0,
            "tức giận": 0,
            "ghê tởm": 0,
            "ngạc nhiên": 0,
            "vui vẻ": 0
        }

        learning_cards = self.emotion_concepts_service.get_all_concepts()

        # Tạo Session domain
        session = Session(
            session_id=uuid4(),
            user_id=user_uuid,
            game_id=game_uuid,
            start_time=datetime.now(),
            state=SessionStateEnum.playing,
            score=0,
            emotion_errors={"sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0},
            max_errors=game.max_errors,
            level_threshold=game.level_threshold,
            ratio=ratio,
            time_limit=game.time_limit,
            questions=questions,
            level=level
        )
        saved_session = self.session_service.create(session)

        return {
            "session_id": str(saved_session.session_id),
            "questions": formatted_questions,
            "max_errors": game.max_errors,
            "time_limit": game.time_limit,
            "emotion_errors": emotion_errors, 
            "learning_cards": learning_cards
        }
    
    def end_session_and_update_progress(self, session_id: UUID, results: List[Dict[str, Any]]) -> Dict:

        session = self.session_service.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        final_score = 0
        emotion_errors = session.emotion_errors
        total_response_time = 0
        total_correct = 0

        for res in results:
            question_uuid = res.get("question_id")
            is_correct = res.get("is_correct", False)

            # Lấy câu hỏi bằng QuestionService
            question = self.question_service.get_question_by_id(question_uuid)
            if not question:
                print(f"Warning: Question {question_uuid} not found.")
                continue

            correct_answer_str = question.correct_answer

            # Lưu session-question
            sq = SessionQuestions(
                id=uuid4(),
                session_id=session_id,
                question_id=question.question_id,
                user_answer={"answer": res.get("answer")},
                correct_answer={"answer": correct_answer_str},
                is_correct=is_correct,
                response_time_ms=res.get("response_time_ms", 0),
                check_hint=False,
                cv_confidence=None,
                timestamp=datetime.now()
            )
            self.session_questions_service.create(sq)

            total_response_time += res.get("response_time_ms", 0)
            if is_correct:
                final_score += 10
                total_correct += 1
            else:
                # emotion gốc chính là correct_answer
                emotion = correct_answer_str
                emotion_errors[emotion] = emotion_errors.get(emotion, 0) + 1

        session.score = final_score
        session.emotion_errors = emotion_errors
        session.state = SessionStateEnum.end
        session.end_time = datetime.now()

        old_error = session.emotion_errors
        # Lấy danh sách các câu hỏi mà user chơi cho tiến trình này
        session_questions_list = self.session_questions_service.get_session_by_id(session.session_id)
        session.questions = session_questions_list

        updated_session = session

        progress = self.child_progress_service.update_progress_after_session(
            child_id=session.user_id,
            game_id=session.game_id,
            session=updated_session,
            old_emotion_error=old_error
        )

        updated_session = self.session_service.update(session)

        return {
            "status": "success",
            "message": "Session ended and progress updated.",
            "final_score": final_score,
            "progress_level": progress.level
        }
