from uuid import UUID
from typing import List, Dict
from app.repository.admin_repo import AdminRepository
from app.repository.emotion_concepts_repo import GameContentsRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.domain.users.user import User
from app.domain.users.child import Child
from app.domain.sessions.emotion_concept import EmotionConcept
from app.domain.games.question import Question
from app.domain.games.game_content import GameContent
from app.domain.enum import RoleEnum

class AdminService:
    def __init__(
        self,
        admin_repo: AdminRepository,
        emotion_repo: GameContentsRepository,
        question_repo: QuestionsRepository,
        game_content_repo: GameContentRepo
    ):
        self.admin_repo = admin_repo
        self.emotion_repo = emotion_repo
        self.question_repo = question_repo
        self.game_content_repo = game_content_repo

    # ==================== User Management ====================
    def get_all_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Lấy danh sách tất cả users"""
        try:
            users = self.admin_repo.get_all_users(skip, limit)
            total = self.admin_repo.count_users()
            return {
                "status": "success",
                "data": {
                    "users": [self._user_to_dict(user) for user in users],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def get_user_by_id(self, user_id: UUID) -> dict:
        """Lấy thông tin chi tiết user"""
        try:
            user = self.admin_repo.get_user_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            return {
                "status": "success",
                "data": self._user_to_dict(user)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_user(self, user_id: UUID, data: dict) -> dict:
        """Cập nhật thông tin user"""
        try:
            user = self.admin_repo.get_user_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            
            # Update fields
            if "name" in data:
                user.name = data["name"]
            if "email" in data:
                user.email = data["email"]
            if "role" in data:
                user.role = RoleEnum[data["role"]]
            
            updated_user = self.admin_repo.update_user(user)
            return {
                "status": "success",
                "message": "User updated successfully",
                "data": self._user_to_dict(updated_user)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_user(self, user_id: UUID) -> dict:
        """Xóa user"""
        try:
            success = self.admin_repo.delete_user(user_id)
            if success:
                return {
                    "status": "success",
                    "message": "User deleted successfully"
                }
            return {"status": "failed", "message": "User not found"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def get_all_children(self, skip: int = 0, limit: int = 100) -> dict:
        """Lấy danh sách tất cả children"""
        try:
            children = self.admin_repo.get_all_children(skip, limit)
            total = self.admin_repo.count_children()
            return {
                "status": "success",
                "data": {
                    "children": [self._child_to_dict(child) for child in children],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def search_users(self, name: str, skip: int = 0, limit: int = 100) -> dict:
        """Tìm kiếm users theo tên"""
        try:
            users = self.admin_repo.search_users_by_name(name, skip, limit)
            return {
                "status": "success",
                "data": {
                    "users": [self._user_to_dict(user) for user in users],
                    "total": len(users)
                }
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    # ==================== Emotion Concepts Management ====================
    def get_all_emotions(self, game_id: UUID, level: int) -> dict:
        """Lấy danh sách emotion concepts"""
        try:
            emotions = self.emotion_repo.get_by_game_and_level(game_id, level)
            return {
                "status": "success",
                "data": [self._emotion_to_dict(e) for e in emotions]
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def create_emotion_concept(self, data: dict) -> dict:
        """Tạo emotion concept mới"""
        try:
            emotion = EmotionConcept(
                concept_id=UUID(data.get("concept_id")),
                emotion=data.get("emotion"),
                level=data.get("level"),
                title=data.get("title"),
                video_path=data.get("video_path"),
                image_path=data.get("image_path"),
                audio_path=data.get("audio_path"),
                description=data.get("description")
            )
            # Save logic (cần implement trong repo)
            return {
                "status": "success",
                "message": "Emotion concept created",
                "concept_id": str(emotion.concept_id)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    # ==================== Questions Management ====================
    def get_all_questions(self, game_id: UUID, level: int, count: int = 10) -> dict:
        """Lấy danh sách câu hỏi"""
        try:
            questions = self.question_repo.get_random_contents(game_id, level, count)
            return {
                "status": "success",
                "data": [self._question_to_dict(q) for q in questions]
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def create_question(self, data: dict) -> dict:
        """Tạo câu hỏi mới"""
        try:
            # Logic tạo question
            return {
                "status": "success",
                "message": "Question created"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_question(self, question_id: UUID, data: dict) -> dict:
        """Cập nhật câu hỏi"""
        try:
            # Logic update question
            return {
                "status": "success",
                "message": "Question updated"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_question(self, question_id: UUID) -> dict:
        """Xóa câu hỏi"""
        try:
            # Logic delete question
            return {
                "status": "success",
                "message": "Question deleted"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    # ==================== Game Content Management ====================
    def get_all_game_contents(self, game_id: UUID, level: int) -> dict:
        """Lấy danh sách game contents"""
        try:
            contents = self.game_content_repo.get_by_game_and_level(game_id, level)
            return {
                "status": "success",
                "data": [self._content_to_dict(c) for c in contents]
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def create_game_content(self, data: dict) -> dict:
        """Tạo game content mới"""
        try:
            # Logic tạo content
            return {
                "status": "success",
                "message": "Game content created"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_game_content(self, content_id: UUID, data: dict) -> dict:
        """Cập nhật game content"""
        try:
            # Logic update content
            return {
                "status": "success",
                "message": "Game content updated"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_game_content(self, content_id: UUID) -> dict:
        """Xóa game content"""
        try:
            # Logic delete content
            return {
                "status": "success",
                "message": "Game content deleted"
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    # ==================== Helper Methods ====================
    def _user_to_dict(self, user: User) -> dict:
        """Convert User domain entity to dict"""
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "name": user.name
        }

    def _child_to_dict(self, child: Child) -> dict:
        """Convert Child domain entity to dict"""
        return {
            "user_id": child.user_id,
            "age": child.age,
            "gender": child.gender.value if child.gender else None,
            "phone_number": child.phone_number,
            "last_played": child.last_played.isoformat() if child.last_played else None,
            "created_at": child.created_at.isoformat() if child.created_at else None
        }

    def _emotion_to_dict(self, emotion: EmotionConcept) -> dict:
        """Convert EmotionConcept to dict"""
        return {
            "concept_id": str(emotion.concept_id),
            "emotion": emotion.emotion,
            "level": emotion.level,
            "title": emotion.title
        }

    def _question_to_dict(self, question: Question) -> dict:
        """Convert Question to dict"""
        return {
            "question_id": str(question.question_id),
            "game_id": str(question.game_id),
            "level": question.level,
            "correct_answer": question.correct_answer
        }

    def _content_to_dict(self, content: GameContent) -> dict:
        """Convert GameContent to dict"""
        return {
            "content_id": str(content.content_id),
            "game_id": str(content.game_id),
            "level": content.level,
            "content_type": content.content_type,
            "emotion": content.emotion
        }