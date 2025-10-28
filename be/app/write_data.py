# write_data.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models.users.user import User
from app.models.users import Child
from app.models.games import Game
from app.models.games.game_content import GameContent
from app.models.games.game_data import GameData
from app.models.games.game_data_contents import GameDataContents
from app.models.games.question import Question
from app.models.games.question_answer_options import QuestionAnswerOptions
from app.models.sessions import Session
from app.models.sessions.session_questions import SessionQuestions
from app.models.analytics.game_history import GameHistory
from app.models.analytics.session_history import SessionHistory
from app.models.sessions.emotion_concept import EmotionConcept
from app.models.analytics.child_progress import ChildProgress
from app.models.analytics.report import Report
import json

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    db = next(get_db())
    try:
        # Thêm dữ liệu mới
        new_user = User(user_id=str(uuid.uuid4()), username="newadmin", email="newadmin@example.com", password="newpass", role="admin", name="New Admin")
        db.add(new_user)
        db.flush()  # Lấy user_id tự động

        new_child = Child(user_id=new_user.user_id, age=12, last_played="2025-10-26 12:00:00", report_preferences="daily", created_at="2025-10-26 12:00:00", last_login=None)
        db.add(new_child)

        new_game = Game(game_id=str(uuid.uuid4()), game_type="GameCV", name="New Game", level=3, difficulty_level=8, max_errors=4, level_threshold=20, time_limit=900)
        db.add(new_game)
        db.flush()

        new_content = GameContent(content_id=str(uuid.uuid4()), game_id=new_game.game_id, level=3, content_type="video", media_path="/videos/new.mp4", question_text="New question", correct_answer="yes", emotion="excited", explanation="New explanation")
        db.add(new_content)

        new_data = GameData(data_id=str(uuid.uuid4()), game_id=new_game.game_id, level=3)
        db.add(new_data)
        db.flush()

        db.add(GameDataContents(data_id=new_data.data_id, content_id=new_content.content_id))

        new_question = Question(question_id=str(uuid.uuid4()), game_id=new_game.game_id, level=3, content_id=new_content.content_id, correct_answer="yes")
        db.add(new_question)

        db.add(QuestionAnswerOptions(question_id=new_question.question_id, content_id=new_content.content_id))

        new_session = Session(session_id=str(uuid.uuid4()), user_id=new_child.user_id, game_id=new_game.game_id, start_time="2025-10-26 12:30:00", end_time=None, state="playing", score=0, emotion_errors=json.dumps({"error": "none"}), max_errors=4, level_threshold=20, ratio=json.dumps([]), time_limit=900, question_ids=json.dumps([]))
        db.add(new_session)
        db.flush()

        new_session_question = SessionQuestions(id=str(uuid.uuid4()), session_id=new_session.session_id, question_id=new_question.question_id, user_answer=json.dumps({"answer": "no"}), correct_answer=json.dumps({"answer": "yes"}), is_correct=False, response_time_ms=1800, check_hint=True, cv_confidence=0.9, timestamp="2025-10-26 12:35:00")
        db.add(new_session_question)

        new_game_history = GameHistory(history_id=str(uuid.uuid4()), user_id=new_child.user_id, session_id=new_session.session_id, game_id=new_game.game_id, score=0, level=3)
        db.add(new_game_history)

        new_session_history = SessionHistory(session_history_id=str(uuid.uuid4()), child_id=new_child.user_id, game_id=new_game.game_id, session_id=new_session.session_id, level=3, start_time="2025-10-26 12:30:00", end_time=None, score=0)
        db.add(new_session_history)

        new_emotion = EmotionConcept(concept_id=str(uuid.uuid4()), emotion="excited", level=3, title="Excitement", video_path="/videos/excited.mp4", image_path="/images/excited.jpg", audio_path="/audio/excited.mp3", description="Feeling of excitement")
        db.add(new_emotion)

        new_progress = ChildProgress(progress_id=str(uuid.uuid4()), child_id=new_child.user_id, game_id=new_game.game_id, level=3, accuracy=0.9, avg_response_time=1800.0, score=0, last_played="2025-10-26 12:30:00", ratio=json.dumps([0.9]), review_emotions=json.dumps([]))
        db.add(new_progress)

        new_report = Report(report_id=str(uuid.uuid4()), child_id=new_child.user_id, report_type="daily", generated_at="2025-10-26 12:40:00", summary="Daily progress", data=json.dumps({"progress": "good"}))
        db.add(new_report)

        # Commit transaction
        db.commit()
        print("Data inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uuid
    main()