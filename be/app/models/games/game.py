from abc import ABC, abstractmethod
from uuid import UUID
from enum import Enum
from typing import Dict, List, Optional
from models.sessions.game_content import GameContent
from models.sessions.game_data import GameData
from models.sessions.session import Session

class GameTypeEnum(str, Enum):
    CLICK = "GameClick"
    CV = "GameCV"

class SessionStateEnum(str, Enum):
    PLAYING = "playing"
    PAUSE = "pause"
    END = "end"

class Game(ABC):
    def __init__(
        self,
        game_id: UUID,
        game_type: GameTypeEnum,
        name: str,
        level: int,
        difficulty_level: int,
        score: int = 0,
        max_errors: int = 3,
        level_threshold: int = 10,
        emotion_errors: Optional[Dict[str, int]] = None,
        ratio: Optional[Dict[int, List[float]]] = None,
        is_hint: bool = False,
        hint: Optional[GameContent] = None,
        game_state: SessionStateEnum = SessionStateEnum.PLAYING,
        time_limit: int = 60,
        question_data: Optional[GameData] = None
    ):
        self._game_id = game_id
        self._game_type = game_type
        self._name = name
        self._level = level
        self._difficulty_level = difficulty_level
        self._score = score
        self._max_errors = max_errors
        self._level_threshold = level_threshold
        self._emotion_errors = emotion_errors or {}
        self._ratio = ratio or {}
        self._is_hint = is_hint
        self._hint = hint
        self._game_state = game_state
        self._time_limit = time_limit
        self._question_data = question_data

    @abstractmethod
    def play(self, session: Session) -> None:
        """Bắt đầu hoặc tiếp tục phiên chơi"""
        pass

    @abstractmethod
    def continue_game(self, session: Session) -> None:
        """Tiếp tục trò chơi từ trạng thái trước"""
        pass

    @abstractmethod
    def pause(self, session: Session) -> None:
        """Tạm dừng phiên chơi và lưu trạng thái"""
        pass

    @abstractmethod
    def end_game(self, session: Session) -> None:
        """Kết thúc phiên chơi"""
        pass

    @abstractmethod
    def provide_hint(self, content: GameContent) -> None:
        """Hiển thị gợi ý từ GameContent"""
        pass

    @abstractmethod
    def check_emotion_errors(self, emotion_errors: Dict[str, int], emotion: str) -> bool:
        """Kiểm tra lỗi cảm xúc"""
        pass

    @abstractmethod
    def show_emotion_concept(self, emotion: str) -> None:
        """Hiển thị khái niệm cảm xúc"""
        pass

    @abstractmethod
    def update_score(self, correct: bool) -> None:
        """Cập nhật điểm số"""
        pass

    @abstractmethod
    def calculate_ratio(self, emotion_errors: Dict[str, int]) -> List[float]:
        """Tính tỷ lệ xuất hiện cảm xúc"""
        pass

    @abstractmethod
    def next_question_level(self, ratio: List[float], game_data: GameData) -> None:
        """Lấy câu hỏi tiếp theo"""
        pass

    @abstractmethod
    def advance_level(self, score: int) -> None:
        """Tăng level nếu đủ điểm"""
        pass

    @abstractmethod
    def reset_emotion_errors(self) -> None:
        """Đặt lại số lỗi cảm xúc khi lên level"""
        pass

    @abstractmethod
    def get_info_game(self, session: Session) -> Dict:
        """Trả về thông tin game từ session"""
        pass

    @abstractmethod
    def get_question_data(self, game_id: UUID, level: int) -> GameData:
        """Lấy dữ liệu câu hỏi theo game_id và level"""
        pass

    @abstractmethod
    def get_data_by_level(self, level: int) -> GameData:
        """Lấy dữ liệu câu hỏi theo level"""
        pass
