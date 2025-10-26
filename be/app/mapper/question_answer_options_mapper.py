# mapper/games/question_answer_options_mapper.py
from app.models.games.question_answer_options import QuestionAnswerOptions
from app.domain.games.question_answer_options import QuestionAnswerOptions as QuestionAnswerOptionsDomain

class QuestionAnswerOptionsMapper:
    @staticmethod
    def to_domain(model: QuestionAnswerOptions) -> QuestionAnswerOptionsDomain:
        if not model:
            return None
        return QuestionAnswerOptionsDomain(
            question_id=model.question_id,
            content_id=model.content_id
        )

    @staticmethod
    def to_model(domain: QuestionAnswerOptionsDomain) -> QuestionAnswerOptions:
        if not domain:
            return None
        return QuestionAnswerOptions(
            question_id=domain.question_id,
            content_id=domain.content_id
        )