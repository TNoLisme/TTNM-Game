from uuid import UUID
from app.models.games.game_content import GameContent as GameContentModel
from app.domain.games.game_content import GameContent
from app.schemas.games.game_contents_schema import GameContentsSchema  # Giả định schema

class GameContentsMapper:
    @staticmethod
    def to_domain(game_content_model: GameContentModel) -> GameContent:
        """Chuyển đổi từ model sang domain entity."""
        if not game_content_model:
            return None
        # Xử lý content_type - có thể là Enum hoặc string
        content_type_value = game_content_model.content_type
        if hasattr(content_type_value, 'value'):
            content_type_value = content_type_value.value
        elif content_type_value is None:
            content_type_value = "text"  # Default
        
        return GameContent(
            content_id=game_content_model.content_id,
            game_id=game_content_model.game_id,
            level=game_content_model.level,
            content_type=content_type_value,
            media_path=game_content_model.media_path,
            question_text=game_content_model.question_text,
            correct_answer=game_content_model.correct_answer,
            emotion=game_content_model.emotion,
            explanation=game_content_model.explanation
        )

    @staticmethod
    def to_model(game_content_domain: GameContent) -> GameContentModel:
        """Chuyển đổi từ domain entity sang model."""
        if not game_content_domain:
            return None
        return GameContentModel(
            content_id=game_content_domain.content_id,
            game_id=game_content_domain.game_id,
            level=game_content_domain.level,
            content_type=game_content_domain.content_type,
            media_path=game_content_domain.media_path,
            question_text=game_content_domain.question_text,
            correct_answer=game_content_domain.correct_answer,
            emotion=game_content_domain.emotion,
            explanation=game_content_domain.explanation
        )

    @staticmethod
    def to_response(game_content_model: GameContentModel) -> GameContentsSchema.GameContentResponse:
        """Chuyển đổi từ model sang response schema."""
        if not game_content_model:
            return None
        return GameContentsSchema.GameContentResponse(
            content_id=game_content_model.content_id,
            game_id=game_content_model.game_id,
            level=game_content_model.level,
            content_type=game_content_model.content_type,
            media_path=game_content_model.media_path,
            question_text=game_content_model.question_text,
            correct_answer=game_content_model.correct_answer,
            emotion=game_content_model.emotion,
            explanation=game_content_model.explanation
        )