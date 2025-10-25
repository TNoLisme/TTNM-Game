from uuid import UUID
from typing import List, Dict

class GameData:
    def __init__(self, data_id: UUID, game_id: UUID, level: int, contents: List[Dict]):
        self.data_id = data_id
        self.game_id = game_id
        self.level = level
        self.contents = contents  # Danh sách GameContent
        self.correct_answers = []  # Tính toán từ questions
        self.options = []  # Tính toán từ question_answer_options

    @classmethod
    def load_data_by_game_and_level(cls, game_id: UUID, level: int) -> 'GameData':
        # Placeholder: cần repository để truy vấn
        return cls(UUID("456f1234-e89b-12d3-a456-426614174000"), game_id, level, [])

    def validate_data(self, data: Dict) -> bool:
        """Kiểm tra tính hợp lệ của dữ liệu."""
        return bool(data.get("contents") and len(data.get("contents", [])) >= 50)

    def get_random_contents(self, count: int) -> List[Dict]:
        """Lấy ngẫu nhiên số lượng nội dung để tạo câu hỏi."""
        if not self.contents or len(self.contents) < count * 5:  # 5 GameContent mỗi câu
            raise ValueError("Not enough contents")
        # Placeholder: cần repository để random và tính toán correct_answers/options
        return self.contents[:count * 5]