from sqlalchemy.orm import configure_mappers
import inspect
import sys

# 1. Import Base class (cần thiết cho tất cả các Models)
from .base import Base

# 2. Import TẤT CẢ các lớp Model để chúng được đăng ký vào SQLAlchemy Registry.
# Việc này giải quyết vấn đề Import Vòng Tròn khi dùng chuỗi trong relationship("TênClass").

# Models -> Users
from .users.user import User
from .users.child import Child

# Models -> Games
from .games.game import Game
from .games.game_content import GameContent
from .games.game_data import GameData
from .games.question import Question
from .games.game_data_contents import GameDataContents
from .games.question_answer_options import QuestionAnswerOptions

# Models -> Sessions
from .sessions.session import Session
from .sessions.emotion_concept import EmotionConcept
from .sessions.session_questions import SessionQuestions

# Models -> Analytics
from .analytics.child_progress import ChildProgress
from .analytics.game_history import GameHistory
from .analytics.report import Report
from .analytics.session_history import SessionHistory

configure_mappers()

__all__ = ['User', 'Session', 'GameHistory', 'Game', 'Base', 'Child', 'GameContent', 'GameData',
           'Question', 'GameDataContents', 'QuestionAnswerOptions', 'EmotionConcept', 'SessionQuestions', 'ChildProgress', 'Report', 'SessionHistory']
