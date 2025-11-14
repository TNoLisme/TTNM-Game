from uuid import UUID
from typing import List
from .game_content import GameContent

class Question:
    def __init__(self, question_id: UUID, game_id: UUID, level: int, content: GameContent, correct_answer: str):
        self.question_id = question_id
        self.game_id = game_id
        self.level = level
        self.content = content
        self.correct_answer = correct_answer

    @classmethod
    def create_question(cls, game_id: UUID, level: int, content: GameContent) -> 'Question':
        """Tạo câu hỏi mới từ nội dung và đáp án."""
        correct_answer = content.correct_answer
        return cls(UUID("789g1234-e89b-12d3-a456-426614174000"), game_id, level, content, correct_answer)

    @classmethod
    def get_random_contents(cls, game_id: UUID, level: int) -> List[GameContent]:
        """Lấy ngẫu nhiên 5 nội dung (1 câu hỏi + 4 đáp án)."""
        # Placeholder: cần repository để truy vấn
        content = GameContent(UUID("123e4567-e89b-12d3-a456-426614174000"), game_id, level, "image", "path/to/image", "What emotion?", "vui", "vui", "Explanation")
        options = [content] * 4  # Placeholder
        return [content] + options

    def validate_question(self) -> bool:
        """Câu hỏi hợp lệ khi có nội dung và đáp án hợp lệ."""
        return (
            self.content is not None
            and bool(self.correct_answer)
            and isinstance(self.correct_answer, str)
        )