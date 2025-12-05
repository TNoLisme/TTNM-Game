from uuid import UUID
from typing import List, Dict, TYPE_CHECKING
from datetime import datetime
import enum

if TYPE_CHECKING:
    from app.domain.analytics.child_progress import ChildProgress
    from app.domain.games.question import Question

class SessionStateEnum(enum.Enum):
    playing = "playing"
    pause = "pause"
    end = "end"

class Session:
    def __init__(
        self,
        session_id: UUID,
        user_id: UUID,
        game_id: UUID,
        start_time: datetime,
        state: SessionStateEnum,
        score: int,
        emotion_errors: Dict[str, int],
        max_errors: int,
        level_threshold: int,
        ratio: List[float],
        time_limit: int,
        questions: List['Question'], 
        level: int
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.game_id = game_id
        self.start_time = start_time
        self.end_time = None
        self.state = state
        self.score = score
        self.emotion_errors = emotion_errors
        self.max_errors = max_errors
        self.level_threshold = level_threshold
        self.ratio = ratio
        self.time_limit = time_limit
        self.questions = questions  # Danh sách 10 câu hỏi random từ đầu level
        self.level = level


