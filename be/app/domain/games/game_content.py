from uuid import UUID
from typing import List, Optional

class GameContent:
    def __init__(self, content_id: UUID, game_id: UUID, level: int, content_type: str, media_path: str,
                 question_text: str, correct_answer: str, emotion: str, explanation: str):
        self.content_id = content_id
        self.game_id = game_id
        self.level = level
        self.content_type = content_type
        self.media_path = media_path
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.emotion = emotion
        self.explanation = explanation

    @classmethod
    def load_content_by_game_and_level(cls, game_id: UUID, level: int) -> List['GameContent']:
        # Placeholder: cần repository để truy vấn
        return [cls(UUID("123e4567-e89b-12d3-a456-426614174000"), game_id, level, "image", "path/to/image", "What emotion?", "vui", "vui", "Explanation")]

    @classmethod
    def get_content_by_emotion(cls, emotion: str) -> List['GameContent']:
        # Placeholder: cần repository để truy vấn
        return [cls(UUID("123e4567-e89b-12d3-a456-426614174000"), UUID("987fcdeb-12a3-4d56-7890-1234567890ab"), 1, "image", "path/to/image", "What emotion?", "vui", emotion, "Explanation")]

    def validate_content(self, content: dict) -> bool:
        """Kiểm tra tính hợp lệ của nội dung."""
        return all(k in content for k in ["media_path", "correct_answer", "emotion"])

    def get_media_path(self) -> str:
        """Trả về đường dẫn file media."""
        return self.media_path