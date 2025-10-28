from uuid import UUID
from typing import List
from app.domain.games.game_content import GameContent

class Question:
    def __init__(self, question_id: UUID, game_id: UUID, level: int, content: GameContent, answer_options: List[GameContent], correct_answer: str):
        self.question_id = question_id
        self.game_id = game_id
        self.level = level
        self.content = content
        self.answer_options = answer_options
        self.correct_answer = correct_answer

    @classmethod
    def create_question(cls, game_id: UUID, level: int, content: GameContent, answer_options: List[GameContent]) -> 'Question':
        """Tạo câu hỏi mới từ nội dung và đáp án."""
        if len(answer_options) != 4:
            raise ValueError("Exactly 4 answer options are required")
        correct_answer = content.correct_answer
        return cls(UUID("789g1234-e89b-12d3-a456-426614174000"), game_id, level, content, answer_options, correct_answer)

    @classmethod
    def get_random_contents(cls, game_id: UUID, level: int) -> List[GameContent]:
        """Lấy ngẫu nhiên 5 nội dung (1 câu hỏi + 4 đáp án)."""
        # Placeholder: cần repository để truy vấn
        content = GameContent(UUID("123e4567-e89b-12d3-a456-426614174000"), game_id, level, "image", "path/to/image", "What emotion?", "vui", "vui", "Explanation")
        options = [content] * 4  # Placeholder
        return [content] + options

    def validate_question(self) -> bool:
        """Kiểm tra câu hỏi có hợp lệ không."""
        return self.content and len(self.answer_options) == 4 and self.correct_answer