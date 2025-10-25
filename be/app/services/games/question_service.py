from uuid import UUID
from .base_game_service import BaseGameService
from domain.games.question import Question
from repository.questions_repo import QuestionRepository

class QuestionService(BaseGameService):
    def __init__(self, question_repo: QuestionRepository):
        super().__init__(question_repo)

    def create(self, data: dict) -> dict:
        question = Question(
            game_id=UUID(data.get("game_id")),
            level=data.get("level"),
            content=data.get("content"),
            answer_options=data.get("answer_options"),
            correct_answer=data.get("correct_answer")
        )
        self.repo.save_question(question)
        return {"status": "success", "message": f"Question for game {question.game_id} created", "question_id": str(question.question_id)}

    def get_by_id(self, question_id: str) -> dict:
        question = self.repo.get_question_by_id(UUID(question_id))
        if question:
            return {"status": "success", "data": {
                "question_id": str(question.question_id),
                "game_id": str(question.game_id),
                "level": question.level
            }}
        return {"status": "failed", "message": "Question not found"}

    def update(self, question_id: str, data: dict) -> dict:
        question = self.repo.get_question_by_id(UUID(question_id))
        if question:
            question.level = data.get("level", question.level)
            question.correct_answer = data.get("correct_answer", question.correct_answer)
            self.repo.update_question(question)
            return {"status": "success", "message": f"Question {question_id} updated"}
        return {"status": "failed", "message": "Question not found"}

    def delete(self, question_id: str) -> dict:
        question = self.repo.get_question_by_id(UUID(question_id))
        if question:
            self.repo.delete_question(UUID(question_id))
            return {"status": "success", "message": f"Question {question_id} deleted"}
        return {"status": "failed", "message": "Question not found"}