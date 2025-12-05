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
from app.services.games.game_play_service import GamePlayService
from app.domain.analytics import ChildProgress

from app.database import SessionLocal # <-- Thay thế bằng import thực tế của SessionLocal
from datetime import datetime
from typing import Generator

TEST_USER_ID = UUID("7B732DC2-21F1-4369-AF77-098668261CBF")
TEST_GAME_ID = UUID("6C2358B3-9720-446A-94A3-111EDF1CE9E1")
def get_test_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Test:
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

    def test(self):
        progress_dict = self.progress_repo.get_progress(TEST_USER_ID, TEST_GAME_ID)
        print("pro:", progress_dict.ratio)

    def test_game_play_service(self):
        g = GamePlayService(self.db)
        print("A1")
        session_start = g.start_session(str(TEST_GAME_ID), 1, str(TEST_USER_ID))
        print("A")
        session_id = session_start["session_id"]
        questions = session_start["questions"]

        print("🔹 Created session:", session_id)

        mock_results = []
        for index, q in enumerate(questions):
            mock_results.append({
                "question_id": q["question_id"],
                "answer": "dummy",
                "is_correct": True if index % 2 == 0 else False,
                "response_time_ms": 500 + index * 10
            })

        print("🔹 Mock results prepared:", mock_results)

        # 3. Gọi end_session
        result = g.end_session_and_update_progress(
            session_id=session_id,
            results=mock_results
        )

        print("\n🔥 END SESSION RESULT:")
        print(result)

        # 4. Kiểm tra session đã update chưa
        updated_session = self.session_repo.get_by_id(UUID(session_id))

        print("\n🔹 Updated session info:")
        print("score:", updated_session.score)
        print("state:", updated_session.state)
        print("emotion_errors:", updated_session.emotion_errors)

        # 5. Kiểm tra dữ liệu session questions
        sq_list = self.session_questions_repo.get_session_by_id(UUID(session_id))
        print("\n🔹 Session Questions saved:", len(sq_list))
        for sq in sq_list:
            print(" -", sq.question_id, "| correct:", sq.is_correct)

        print("\n✔ test_end_session chạy thành công!")

    def test_update_progress(self):
        x = self.progress_repo.get_progress(TEST_USER_ID, TEST_GAME_ID)
        print("Pro cũ: ", x.ratio, " và ", x.review_emotions)
        if x: 
            progress = ChildProgress(
                progress_id=UUID("1A635D64-5D47-4B19-AE12-BCEEBDB50269"),
                child_id=TEST_USER_ID,
                game_id=TEST_GAME_ID,
                level=3,
                accuracy=float(0.6),
                avg_response_time=float(1),
                score=60,
                last_played=datetime.now(),
                ratio=[0.1, 0.1667+0.1667, 0.1, 0.1667, 0.1667, 0.1665],
                review_emotions=["hay, cảm xúc quá hả ạ"]
            )
            r = self.progress_repo.update(progress)
            if r:
                print("alo", r.ratio)

    def get_last_session(self):
        session = self.session_repo.get_latest_session(TEST_USER_ID, TEST_GAME_ID)
        print("review: ", session.emotion_errors)
        session

def run_all_tests():
    db_generator = get_test_session()
    db = next(db_generator) 
    
    try:
        test_runner = Test(db)
        # test_runner.test_game_play_service()
        # test_runner.test_update_progress()
        test_runner.get_last_session()

    except Exception as e:
        print(f"\n!!! LỖI QUAN TRỌNG TRONG QUÁ TRÌNH TEST: {e} !!!")
        db.rollback() 
        
    finally:
        db_generator.close()


if __name__ == "__main__":
    run_all_tests()

"""
lưu câu hỏi vào session question sau khi hoàn thành chơi 1 level
lưu tổng kết game của level đó vào session history
cập nhật phiên chơi (session)
cập nhật child progress (cập nhật level, ratio, review emotion, end time, score, ..
cập nhật game history


lỗi khi lưu từ vựng: dấu câu"""