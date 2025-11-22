# # app/services/games/recognize_emotion_service.py
# from uuid import UUID
# from typing import List, Dict
# from sqlalchemy.orm import Session
# from app.domain.games.game import GameRecognizeEmotion
# from app.domain.sessions.session import Session
# from app.repository.games_repo import GamesRepository
# from app.repository.game_contents_repo import GameContentsRepository
# from app.repository.game_data_repo import GameDataRepository
# from app.repository.child_progress_repo import ChildProgressRepository
# from app.repository.sessions_repo import SessionsRepository
# from app.repository.session_questions_repo import SessionQuestionsRepository
# from app.current_user import get_current_user
# from app.repository.users_repo import UsersRepository
# import random
# from datetime import datetime

# class RecognizeEmotionService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.user_repo = UsersRepository(db)
#         self.games_repo = GamesRepository(db)
#         self.contents_repo = GameContentsRepository(db)
#         self.game_data_repo = GameDataRepository(db)
#         self.progress_repo = ChildProgressRepository(db)
#         self.session_repo = SessionsRepository(db)
#         self.session_questions_repo = SessionQuestionsRepository(db)

#     def get_progress(self, game_id: str, user_id: str) -> int:
#         progress = self.progress_repo.get_progress(user_id, game_id)
#         return progress.level if progress else 1

#     def validate_level(self, game_id: str, level: int, user_id: str) -> bool:
#         current = self.get_progress(game_id, user_id)
#         return 1 <= level <= current

#     def _select_contents_by_ratio(self, game_id: str, level: int, ratio: List[Dict]) -> List:
#         final_list = []
#         for r in ratio:
#             emotion = r["emotion"]
#             count = r["weight"]

#             group = self.contents_repo.get_by_emotion_and_level(game_id, level, emotion)

#             if len(group) > count:
#                 sampled = random.sample(group, count)
#             else:
#                 sampled = group

#             final_list.extend(sampled)

#         # Nếu còn thiếu → bổ sung cho đủ 10 content
#         if len(final_list) < 10:
#             extra = self.contents_repo.get_by_game_and_level(game_id, level)
#             need = 10 - len(final_list)
#             extra_sampled = random.sample(extra, min(len(extra), need))
#             final_list.extend(extra_sampled)

#         random.shuffle(final_list)
#         return final_list[:10]
    
#     def _generate_question_items(self, contents: List) -> List[Dict]:
#         questions = []

#         for idx, main_content in enumerate(contents):
#             # Đáp án đúng
#             correct_answer = main_content.correct_answer

#             # Chọn các content khác làm nhiễu
#             distractors = [c for c in contents if c.content_id != main_content.content_id]

#             # Lấy 3 đáp án sai
#             if len(distractors) >= 3:
#                 distractor_items = random.sample(distractors, 3)
#             else:
#                 distractor_items = distractors

#             choices = [correct_answer] + [c.correct_answer for c in distractor_items]
#             random.shuffle(choices)

#             questions.append({
#                 "question_id": str(UUID()),
#                 "content_id": str(main_content.content_id),
#                 "question_text": main_content.question_text,
#                 "media_path": main_content.media_path,
#                 "choices": choices,       # danh sách đáp án
#                 "correct_answer": correct_answer,
#                 "hint": main_content.explanation
#             })

#         return questions
    
#     def start_session(self, game_id: str, level: int, user_id: str) -> Dict:
#         if not self.validate_level(game_id, level):
#             raise ValueError("Level không hợp lệ")

#         game = self.games_repo.get_by_id(game_id)

#        # Lấy tỉ lệ cảm xúc
#         progress = self.progress_repo.get_by_user_game(user_id, game_id)
#         ratio = progress.ratio if progress else [{"emotion": "vui", "weight": 10}]

#         # Lấy content theo ratio
#         contents = self._select_contents_by_ratio(game_id, level, ratio)

#         # Tạo danh sách câu hỏi
#         questions = self._generate_question_items(contents)

#         # Lưu session
#         session = Session(
#             session_id=UUID(),
#             user_id=UUID(user_id),
#             game_id=UUID(game_id),
#             start_time=datetime.now(),
#             state="playing",
#             score=0,
#             max_errors=game.max_errors,
#             level_threshold=game.level_threshold,
#             time_limit=game.time_limit,
#             question_ids=[q["question_id"] for q in questions]
#         )
#         self.session_repo.save(session)

#         # Lưu từng câu hỏi vào session_question
#         for q in questions:
#             self.session_questions_repo.create_question(
#                 session_id=session.session_id,
#                 question_id=q["question_id"],
#                 correct_answer=q["correct_answer"],
#                 content_id=q["content_id"]
#             )

#         return {
#             "session_id": str(session.session_id),
#             "questions": questions,
#             "max_errors": game.max_errors
#         }


#     def submit_answer(self, session_id: str, question_id: str, answer: str) -> Dict:
#         sq = self.session_questions_repo.get_by_session_and_question(session_id, question_id)
#         correct = answer == sq.correct_answer
#         sq.user_answer = answer
#         sq.is_correct = correct
#         sq.timestamp = datetime.now()
#         self.session_questions_repo.save(sq)

#         # Cập nhật score
#         session = self.session_repo.get_by_id(session_id)
#         session.score += 10 if correct else 0
#         self.session_repo.save(session)

#         return {"correct": correct, "correct_answer": sq.correct_answer}