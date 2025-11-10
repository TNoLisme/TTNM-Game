from uuid import UUID
from app.models.games.question import Question as QuestionModel
from app.domain.games.question import Question
from app.mapper.game_contents_mapper import GameContentsMapper
from app.schemas.games.question_schema import QuestionSchema  # Giả định schema

class QuestionsMapper:
    @staticmethod
    def to_domain(question_model: QuestionModel) -> Question:
        """Chuyển đổi từ model sang domain entity."""
        if not question_model:
            return None
        content = GameContentsMapper.to_domain(question_model.content)
        answer_options = [GameContentsMapper.to_domain(content) for content in question_model.answer_options]
        return Question(
            question_id=question_model.question_id,
            game_id=question_model.game_id,
            level=question_model.level,
            content=content,
            correct_answer=question_model.correct_answer
        )

    @staticmethod
    def to_model(question_domain: Question) -> QuestionModel:
        """Chuyển đổi từ domain entity sang model."""
        if not question_domain:
            return None
        return QuestionModel(
            question_id=question_domain.question_id,
            game_id=question_domain.game_id,
            level=question_domain.level,
            content_id=question_domain.content.content_id,
            correct_answer=question_domain.correct_answer
        )

    @staticmethod
    def to_response(question_model: QuestionModel) -> QuestionSchema.QuestionResponse:
        """Chuyển đổi từ model sang response schema."""
        if not question_model:
            return None
        return QuestionSchema.QuestionResponse(
            question_id=question_model.question_id,
            game_id=question_model.game_id,
            level=question_model.level,
            content=GameContentsMapper.to_response(question_model.content),
            correct_answer=question_model.correct_answer
        )