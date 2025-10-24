from uuid import UUID
from datetime import datetime
from typing import List, Optional
from models.sessions.game_content import GameContent

class GameData:
    """
    Lưu trữ dữ liệu câu hỏi hoàn chỉnh.
    """

    def __init__(
        self,
        data_id: UUID,
        game_id: UUID,
        level: int,
        contents: Optional[List[GameContent]] = None,
        correct_answers: Optional[List[str]] = None,
        options: Optional[List[str]] = None,
        created_at: datetime = None
    ):
        self._data_id = data_id
        self._game_id = game_id
        self._level = level
        self._contents = contents or []
        self._correct_answers = correct_answers or []
        self._options = options or []
        self._created_at = created_at

    def load_data_by_game_and_level(self, game_id: UUID, level: int) -> "GameData":
        """
        Tải dữ liệu game theo game_id và level.
        """
        pass

    def validate_data(self, data: dict) -> bool:
        """
        Kiểm tra tính hợp lệ của dữ liệu.
        """
        pass

    def get_random_contents(self) -> List[GameContent]:
        """
        Lấy ngẫu nhiên một số nội dung để chơi.
        """
        pass
