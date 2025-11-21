from uuid import UUID, uuid4
from typing import List, Optional, Dict
import random

# Domain
from app.domain.games.game_content import GameContent
from app.domain.games.question import Question
from app.domain.games.game_data import GameData
from app.domain.games.game_data_question import GameDataContents as GameDataContentsDomain

# Repositories
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.game_data_repo import GameDataRepository
from app.repository.game_data_contents_repo import GameDataContentsRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.child_progress_repo import ChildProgressRepository

class QuestionService:
    def __init__(self, db):
        self.contents_repo = GameContentsRepository(db)
        self.game_data_repo = GameDataRepository(db)
        self.game_data_contents_repo = GameDataContentsRepository(db)
        self.questions_repo = QuestionsRepository(db)
        self.progress_repo = ChildProgressRepository(db)

    # Lấy question từ cache hoặc generate mới
    def get_or_generate_questions(
        self, user_id: UUID, game_id: UUID, level: int, ratio: List[float]
    ) -> List[Question]:

        # Check cache
        questions = self._get_cached_questions(user_id, game_id, level)
        if questions:
            print(f"[QuestionService] Cache HIT for user {user_id} | game {game_id}")
            return questions

        # Không có cache => generate mới
        print(f"[QuestionService] Cache MISS for user {user_id} | game {game_id}. Generating new questions.")
        return self._generate_new_questions(user_id, game_id, level, ratio)

    def get_question_by_id(self, question_id: UUID) -> Optional[Question]:
        questions = self.questions_repo.get_by_question_ids([question_id])
        return questions[0] if questions else None

    # Format question cho FE
    def format_questions_for_frontend(self, questions: List[Question], game_id: UUID, level: int) -> List[Dict]:
        formatted_questions = []
        options_pool = self.contents_repo.get_game_content_by_level(game_id, level)

        for q in questions:
            if not q.content:
                print(f"Warning: Question {q.question_id} missing content")
                continue

            main_content = q.content
            correct_answer = q.correct_answer

            distractors = [
                opt for opt in options_pool
                if opt.correct_answer != correct_answer and opt.content_id != main_content.content_id
            ]
            selected_distractors = random.sample(distractors, min(len(distractors), 3))
            options_domain = [main_content] + selected_distractors
            random.shuffle(options_domain)

            options_response = [
                {
                    "content_id": str(opt.content_id),
                    "media_path": opt.media_path,
                    "answer_text": opt.correct_answer
                }
                for opt in options_domain
            ]

            formatted_questions.append({
                "question_id": str(q.question_id),
                "question_text": main_content.question_text,
                "media_path": main_content.media_path,
                "options": options_response,
                "correct_answer": correct_answer,
                "explanation": main_content.explanation
            })

        return formatted_questions

    # lấy các question nếu đã có bộ câu hỏi
    def _get_cached_questions(self, user_id: UUID, game_id: UUID, level: int) -> Optional[List[Question]]:
        game_data = self.game_data_repo.load_data_by_game_and_level(game_id, user_id, level)
        if not game_data or not game_data.data_id:
            return None

        question_ids = self.game_data_contents_repo.get_question_ids_by_data_id(game_data.data_id)
        questions = self.questions_repo.get_by_question_ids(question_ids)
        return questions

    # generate question mới
    def _generate_new_questions(self, user_id: UUID, game_id: UUID, level: int, ratio: List[float]) -> List[Question]:
        emotions = ["Vui vẻ", "Buồn bã", "Tức giận", "Sợ hãi", "Ngạc nhiên", "Ghê tởm"]
        counts = [round(r * 5) for r in ratio]

        while sum(counts) > 5:
            counts[counts.index(max(counts))] -= 1
        while sum(counts) < 5:
            counts[counts.index(min(counts))] += 1

        main_contents: List[GameContent] = []
        for i, emotion in enumerate(emotions):
            cnt = counts[i]
            if cnt == 0: continue
            candidates = self.contents_repo.get_game_content_by_emotion_and_level(game_id, level, emotion)
            selected = random.sample(candidates, min(len(candidates), cnt))
            main_contents.extend(selected)

        # Nếu chưa đủ số lượng câu hỏi
        if len(main_contents) < 5:
            needed = 5 - len(main_contents)
            all_contents = self.contents_repo.get_game_content_by_level(game_id, level)
            existing_ids = {c.content_id for c in main_contents}
            extra_candidates = [c for c in all_contents if c.content_id not in existing_ids]
            selected_extra = random.sample(extra_candidates, min(len(extra_candidates), needed))
            main_contents.extend(selected_extra)

        main_contents = main_contents[:5]

        if not main_contents:
            raise ValueError(f"No GameContent found for game {game_id} level {level}")

        # Tạo game data record
        new_data = GameData(data_id=uuid4(), game_id=game_id, user_id=user_id, level=level, questions=[])
        saved_data = self.game_data_repo.create(new_data)

        list_of_questions: List[Question] = []
        for content in main_contents:
            question = self.questions_repo.get_or_create_by_content(content)
            link = GameDataContentsDomain(data_id=saved_data.data_id, question_id=question.question_id)
            self.game_data_contents_repo.create(link)
            list_of_questions.append(question)

        return list_of_questions
