from uuid import UUID, uuid4
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
import random
import json

# Domain
from app.domain.sessions.session import Session, SessionStateEnum
from app.domain.games.game_data import GameData
from app.domain.games.game_content import GameContent
from app.domain.games.question import Question
from app.domain.games.game_data_question import GameDataContents as GameDataContentsDomain
from app.domain.sessions.session_questions import SessionQuestions

# Repositories
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.game_data_repo import GameDataRepository
from app.repository.game_data_contents_repo import GameDataContentsRepository
from app.repository.child_progress_repo import ChildProgressRepository
from app.repository.sessions_repo import SessionsRepository
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.repository.questions_repo import QuestionsRepository
# Service (để cập nhật progress)
from app.services.analytics.child_progress_service import ChildProgressService


class GamePlayService:
    def __init__(self, db: Session):
        self.db = db
        self.games_repo = GamesRepository(db)
        self.contents_repo = GameContentsRepository(db)
        self.game_data_repo = GameDataRepository(db)
        self.progress_repo = ChildProgressRepository(db)
        self.session_repo = SessionsRepository(db)
        self.session_questions_repo = SessionQuestionsRepository(db)
        self.game_data_contents_repo = GameDataContentsRepository(db)
        self.questions_repo = QuestionsRepository(db)
        self.child_progress_service = ChildProgressService(self.progress_repo)


    # bắt đầu 1 phiên chơi (chơi 1 level của game)
    def start_session(self, game_id: str, level: int, user_id: str) -> Dict:
        game_uuid = UUID(game_id)
        user_uuid = UUID(user_id)
        
        game = self.games_repo.get_game_by_id(game_uuid)
        if not game:
            raise ValueError(f"Game not found with ID: {game_id}")

        # lấy mảng ratio + câu hỏi cho level của game
        ratio = self._get_or_create_ratio(user_uuid, game_uuid)
        main_questions = self._get_cached_questions(user_uuid, game_uuid, level)
        # nếu k có list question thì tạo mới
        if not main_questions:
            print(f"[GamePlayService] Cache MISS for user {user_id} | game {game_id}. Generating new questions.")
            main_questions = self._generate_new_questions(user_uuid, game_uuid, level, ratio)
        else:
            print(f"[GamePlayService] Cache HIT for user {user_id} | game {game_id}. Reusing questions.")

        questions_for_frontend = self._format_questions_for_frontend(main_questions, game_uuid, level)
        level_game = level
        session = Session(
            session_id=uuid4(),
            user_id=user_uuid,
            game_id=game_uuid,
            start_time=datetime.now(),
            state=SessionStateEnum.playing,
            score=0,
            emotion_errors={},
            max_errors=game.max_errors,
            level_threshold=game.level_threshold,
            ratio=[0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665],
            time_limit=game.time_limit,
            questions=main_questions,
            level=level_game
        )
        saved_session = self.session_repo.create(session)

        return {
            "session_id": str(saved_session.session_id),
            "questions": questions_for_frontend,
            "max_errors": game.max_errors,
            "time_limit": game.time_limit
        }

    def end_session_and_update_progress(self, session_id: str, results: List[Dict[str, Any]]) -> Dict:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        final_score = 0
        emotion_errors = {}
        total_response_time = 0
        total_correct = 0

        for res in results:
            print("question_id type:", type(res.get("question_id")), res.get("question_id"))

            question_uuid = res.get("question_id")
            is_correct = res.get("is_correct", False)
            question_domain_list = self.questions_repo.get_by_question_ids([question_uuid])
            if not question_domain_list:
                print(f"Warning: Question {question_uuid} not found. Skipping result.")
                continue
                
            question_domain = question_domain_list[0]
            correct_answer_str = question_domain.correct_answer

            sq = SessionQuestions(
                id=uuid4(),
                session_id=session_id,
                question_id=question_domain.question_id,
                user_answer={"answer": res.get("answer")},
                correct_answer={"answer": correct_answer_str},
                is_correct=is_correct,
                response_time_ms=res.get("response_time_ms", 0),
                check_hint=False, # cần thêm biến checkhint bên fe
                cv_confidence=None,
                timestamp=datetime.now()
            )
            self.session_questions_repo.create(sq)
            total_response_time += res.get("response_time_ms", 0)
            if is_correct:
                final_score += 10 
                total_correct += 1
            else:
                emotion_missed = correct_answer_str
                emotion_errors[emotion_missed] = emotion_errors.get(emotion_missed, 0) + 1
        
        session.score = final_score
        session.emotion_errors = emotion_errors
        session.state = SessionStateEnum.end
        session.end_time = datetime.now()
        
        updated_session = self.session_repo.update(session)

        accuracy = (total_correct / len(results)) * 100 if results else 0
        avg_time = (total_response_time / len(results)) if results else 0
    

        progress_domain = self.child_progress_service.update_progress_after_session(
            child_id=session.user_id,
            game_id=session.game_id,
            session=updated_session
        )
        
        return {
            "status": "success",
            "message": "Session ended and progress updated.",
            "final_score": final_score,
            "progress_level": progress_domain.level
        }


    # Lấy mảng ratio của user theo từng game 
    def _get_or_create_ratio(self, user_id: UUID, game_id: UUID) -> List[float]:
        progress = self.progress_repo.get_progress(user_id, game_id)
        default_ratio = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665] # 6 cảm xúc
        
        # Kiểm tra nếu ratio rỗng hoặc toàn 0
        if not progress or not progress.ratio or all(r == 0 for r in progress.ratio):
            return default_ratio
        return progress.ratio

    # lấy list question theo level game của user
    def _get_cached_questions(self, user_id: UUID, game_id: UUID, level: int) -> Optional[List[Question]]:
        # lấy data_id nếu game đó đã được tạo list question
        game_data = self.game_data_repo.load_data_by_game_and_level(game_id, user_id, level)
        if game_data and game_data.data_id:
            # lấy list các question_id ở table game_data_question (code là game data content)
            main_question_ids = self.game_data_contents_repo.get_question_ids_by_data_id(game_data.data_id)
            # lấy các question theo question_id ở table question
            main_questions = self.questions_repo.get_by_question_ids(main_question_ids)
            
            return main_questions
        return None

    # Tạo list question cho level game dựa trên ratio của user
    def _generate_new_questions(self, user_id: UUID, game_id: UUID, level: int, ratio: List[float]) -> List[Question]:
        emotions = ["Vui vẻ", "Buồn bã", "Tức giận", "Sợ hãi", "Ngạc nhiên", "Ghê tởm"] # 6 emotions
        
        counts = [round(r * 5) for r in ratio]
        # Đảm bảo đủ đúng số lượng question
        while sum(counts) > 5:
            counts[counts.index(max(counts))] -= 1
        while sum(counts) < 5:
            counts[counts.index(min(counts))] += 1

        main_contents: List[GameContent] = []
        for i, emotion in enumerate(emotions):
            count = counts[i]
            if count == 0: continue
            # lấy tất cả các content phù hợp với level của emotion cho game
            candidates = self.contents_repo.get_game_content_by_emotion_and_level(game_id, level, emotion)
            # chọn random các câu hỏi theo cảm xúc đó
            selected = random.sample(candidates, min(len(candidates), count))
            main_contents.extend(selected)
        
        # Nếu chưa đủ số lượng câu hỏi
        if len(main_contents) < 5:
             needed = 5 - len(main_contents)
             # lấy tất cả các content theo level đó k theo cảm xúc nào
             all_contents = self.contents_repo.get_game_content_by_level(game_id, level)
             # Tạo set để lọc id
             existing_ids = {c.content_id for c in main_contents}
             # bỏ các id đã được thêm vào main_contents
             extra_candidates = [c for c in all_contents if c.content_id not in existing_ids]
             selected_extra = random.sample(extra_candidates, min(len(extra_candidates), needed))
             main_contents.extend(selected_extra)

        main_contents = main_contents[:5]

        if not main_contents:
            raise ValueError(f"Không tìm thấy bất kỳ GameContent nào cho game {game_id} level {level}.")
        
        
        new_data = GameData(data_id=uuid4(), game_id=game_id, user_id=user_id, level=level, questions=[])
        # tạo các bản ghi mới trong table game data
        saved_data = self.game_data_repo.create(new_data)

        list_of_questions: List[Question] = []
        #  tạo các bản ghi trong các table question và game data question
        for content in main_contents:
            question = self.questions_repo.get_or_create_by_content(content) # trả về domain Question
            link = GameDataContentsDomain(data_id=saved_data.data_id, question_id=question.question_id)
            self.game_data_contents_repo.create(link)
            list_of_questions.append(question)
            
        return list_of_questions

    # cấu trúc cho 1 câu: 1 câu hỏi với 4 đáp án ngẫu nhiên cùng level.
    def _format_questions_for_frontend(self, main_questions: List[Question], game_id: UUID, level: int) -> List[Dict]:
        formatted_questions = []
        options_pool = self.contents_repo.get_game_content_by_level(game_id, level)
        
        for main_question in main_questions:
            if not main_question.content:
                 print(f"Warning: Question {main_question.question_id} is missing content.")
                 continue
                 
            main_content = main_question.content 
            correct_answer = main_question.correct_answer
            
            distractors = [
                opt for opt in options_pool 
                if opt.correct_answer != correct_answer and opt.content_id != main_content.content_id
            ]
            selected_distractors = random.sample(distractors, min(len(distractors), 3))
            
            options_domain = [main_content] + selected_distractors
            random.shuffle(options_domain)
            
            options_response = [
                {
                    "content_id": str(opt.content_id),
                    "media_path": opt.media_path,
                    "answer_text": opt.correct_answer 
                } for opt in options_domain
            ]
            
            formatted_questions.append({
                "question_id": str(main_question.question_id),
                "question_text": main_content.question_text,
                "media_path": main_content.media_path,
                "options": options_response,
                "correct_answer": correct_answer,
                "explanation": main_content.explanation
            })
            
        return formatted_questions