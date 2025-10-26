# read_data.py
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
        # Lấy dữ liệu từ tất cả các bảng
        users = db.query(User).all()
        children = db.query(Child).all()
        games = db.query(Game).all()
        game_contents = db.query(GameContent).all()
        game_data = db.query(GameData).all()
        game_data_contents = db.query(GameDataContents).all()
        questions = db.query(Question).all()
        question_answer_options = db.query(QuestionAnswerOptions).all()
        sessions = db.query(Session).all()
        session_questions = db.query(SessionQuestions).all()
        game_history = db.query(GameHistory).all()
        session_history = db.query(SessionHistory).all()
        emotion_concepts = db.query(EmotionConcept).all()
        child_progress = db.query(ChildProgress).all()
        reports = db.query(Report).all()

        # In kết quả
        print("Users:", len(users))

        print("\nChildren:", len(children))

        print("\nGames:", len(games))

        print("\nGame Contents:", len(game_contents))

        print("\nGame Data:", len(game_data))

        print("\nGame Data Contents:", len(game_data_contents))

        print("\nQuestions:", len(questions))

        print("\nQuestion Answer Options:", len(question_answer_options))

        print("\nSessions:", len(sessions))

        print("\nSession Questions:", len(session_questions))

        print("\nGame History:", len(game_history))

        print("\nSession History:", len(session_history))

        print("\nEmotion Concepts:", len(emotion_concepts))

        print("\nChild Progress:", len(child_progress))

        print("\nReports:", len(reports))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()