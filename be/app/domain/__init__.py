# app/domain/__init__.py
from sqlalchemy.orm import configure_mappers
from .analytics import ChildProgress, GameHistory, Report, SessionHistory
from .events import GameCompleted, LevelAdvanced, ProgressUpdated, SessionEnded, SessionStarted
from .games import Game, GameContent, GameData, Question, GameDataContents, QuestionAnswerOptions
from .sessions import EmotionConcept, Session, SessionQuestions
from .users import Admin, Child, User
from .enum import RoleEnum, GameTypeEnum, ReportTypeEnum, SessionStateEnum

configure_mappers()

__all__ = ['ChildProgress', 'GameHistory', 'Report', 'SessionHistory',
           'GameCompleted', 'LevelAdvanced', 'ProgressUpdated', 'SessionEnded', 'SessionStarted',
           'Game', 'GameContent', 'GameData', 'Question',
           'GameDataContents', 'QuestionAnswerOptions',
           'EmotionConcept', 'Session', 'SessionQuestions',
           'Admin', 'Child', 'User', 'RoleEnum', 'GameTypeEnum', 'ReportTypeEnum', 'SessionStateEnum']