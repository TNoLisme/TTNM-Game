# domain/games/question_answer_options.py
class QuestionAnswerOptions:
    def __init__(self, question_id: str, content_id: str):
        self.question_id = question_id
        self.content_id = content_id

    def __repr__(self):
        return f"QuestionAnswerOptions(question_id={self.question_id}, content_id={self.content_id})"