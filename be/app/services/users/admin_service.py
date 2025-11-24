from uuid import uuid4, UUID
from typing import List, Dict, Optional
from datetime import datetime
from app.repository.admin_repo import AdminRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository
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
        emotion_repo: EmotionConceptRepository,
        question_repo: QuestionsRepository,
        game_content_repo: GameContentsRepository
    ):
        self.admin_repo = admin_repo
        self.emotion_repo = emotion_repo
        self.question_repo = question_repo
        self.game_content_repo = game_content_repo

    # ==================== User Management ====================
    def _user_to_dict(self, user) -> dict:
        """Convert User object to dictionary"""
        user_dict = {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        }
        
        # Nếu có thêm các thuộc tính khác trong User model
        if hasattr(user, 'status'):
            user_dict["status"] = user.status
        if hasattr(user, 'created_at'):
            user_dict["created_at"] = user.created_at.isoformat() if user.created_at else None
            
        return user_dict
    
    # ✅ Hoặc nếu cần đầy đủ thông tin child
    def _user_to_dict_full(self, user, child=None) -> dict:
        """Convert User object (with optional Child data) to dictionary"""
        user_dict = {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        }
        
        # Nếu có child data, thêm vào
        if child:
            user_dict.update({
                "age": child.age,
                "gender": child.gender,
                "date_of_birth": child.date_of_birth.isoformat() if child.date_of_birth else None,
                "phone_number": child.phone_number,
                "last_played": child.last_played.isoformat() if child.last_played else None,
                "report_preferences": child.report_preferences,
                "created_at": child.created_at.isoformat() if child.created_at else None,
                "last_login": child.last_login.isoformat() if child.last_login else None,
            })
        
        return user_dict
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> dict:
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

def create_user(self, data: dict) -> dict:
    try:
        # Kiểm tra username đã tồn tại
        existing_user = self.admin_repo.get_user_by_username(data["username"])
        if existing_user:
            return {"status": "failed", "message": "Username đã tồn tại"}

        # Kiểm tra email đã tồn tại
        existing_email = self.admin_repo.get_user_by_email(data["email"])
        if existing_email:
            return {"status": "failed", "message": "Email đã tồn tại"}

        # Tạo user mới - password không hash theo SQL schema
        user = User(
            user_id=uuid4(),
            username=data["username"],
            email=data["email"],
            name=data["name"],
            role=RoleEnum[data["role"]],
            password=data["password"]
        )

        self.admin_repo.add_user(user)

        # Nếu role là 'child', tạo thêm record trong bảng children
        if data["role"] == "child":
            # ✅ Thêm 3 tham số bắt buộc: gender, date_of_birth, phone_number
            child = Child(
                user_id=user.user_id,
                gender=data.get("gender", "other"),  # ✅ Bắt buộc, default = "other"
                date_of_birth=data.get("date_of_birth"),  # ✅ Bắt buộc
                phone_number=data.get("phone_number", ""),  # ✅ Bắt buộc, default = ""
                age=data.get("age"),
                last_played=None,
                report_preferences=data.get("report_preferences", "weekly"),
                created_at=datetime.now(),
                last_login=None
            )
            self.admin_repo.add_child(child)

        return {
            "status": "success",
            "message": "User created successfully",
            "data": self._user_to_dict(user)
        }

    except KeyError as e:
        return {"status": "failed", "message": f"Missing required field: {str(e)}"}
    except Exception as e:
        return {"status": "failed", "message": str(e)}
        
    def update_user(self, user_id: UUID, data: dict) -> dict:
        try:
            user = self.admin_repo.get_user_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            
            # Update fields theo SQL schema
            if "name" in data:
                user.name = data["name"]
            if "email" in data:
                # Kiểm tra email mới có trùng với user khác không
                existing_email = self.admin_repo.get_user_by_email(data["email"])
                if existing_email and existing_email.user_id != user_id:
                    return {"status": "failed", "message": "Email đã được sử dụng"}
                user.email = data["email"]
            if "role" in data:
                user.role = RoleEnum[data["role"]]
            if "password" in data:
                user.password = data["password"]
            
            updated_user = self.admin_repo.update_user(user)
            return {
                "status": "success",
                "message": "User updated successfully",
                "data": self._user_to_dict(updated_user)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_user(self, user_id: UUID) -> dict:
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
        try:
            # Theo SQL schema, emotion_concepts không có game_id
            emotions = self.emotion_repo.get_by_level(level)
            return {
                "status": "success",
                "data": [self._emotion_to_dict(e) for e in emotions]
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def create_emotion_concept(self, data: dict) -> dict:
        try:
            concept_id = uuid4() if "concept_id" not in data else UUID(data["concept_id"])
            
            emotion = EmotionConcept(
                concept_id=concept_id,
                emotion=data["emotion"],
                level=data["level"],
                title=data["title"],
                video_path=data.get("video_path"),
                image_path=data.get("image_path"),
                audio_path=data.get("audio_path"),
                description=data.get("description")
            )
            
            self.emotion_repo.add(emotion)
            
            return {
                "status": "success",
                "message": "Emotion concept created successfully",
                "data": self._emotion_to_dict(emotion)
            }
        except KeyError as e:
            return {"status": "failed", "message": f"Missing required field: {str(e)}"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_emotion_concept(self, concept_id: UUID, data: dict) -> dict:
        try:
            emotion = self.emotion_repo.get_by_id(concept_id)
            if not emotion:
                return {"status": "failed", "message": "Emotion concept not found"}
            
            # Update fields
            if "emotion" in data:
                emotion.emotion = data["emotion"]
            if "level" in data:
                emotion.level = data["level"]
            if "title" in data:
                emotion.title = data["title"]
            if "video_path" in data:
                emotion.video_path = data["video_path"]
            if "image_path" in data:
                emotion.image_path = data["image_path"]
            if "audio_path" in data:
                emotion.audio_path = data["audio_path"]
            if "description" in data:
                emotion.description = data["description"]
            
            updated_emotion = self.emotion_repo.update(emotion)
            return {
                "status": "success",
                "message": "Emotion concept updated successfully",
                "data": self._emotion_to_dict(updated_emotion)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_emotion_concept(self, concept_id: UUID) -> dict:
        try:
            success = self.emotion_repo.delete(concept_id)
            if success:
                return {
                    "status": "success",
                    "message": "Emotion concept deleted successfully"
                }
            return {"status": "failed", "message": "Emotion concept not found"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    # ==================== Questions Management ====================
    def get_all_questions(self, game_id: UUID, level: int, count: int = 10) -> dict:
        try:
            questions = self.question_repo.get_random_contents(game_id, level, count)
            return {
                "status": "success",
                "data": [self._question_to_dict(q) for q in questions]
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def create_question(self, data: dict) -> dict:
        try:
            question_id = uuid4() if "question_id" not in data else UUID(data["question_id"])
            
            question = Question(
                question_id=question_id,
                game_id=UUID(data["game_id"]),
                level=data["level"],
                content_id=UUID(data["content_id"]),
                correct_answer=data["correct_answer"]
            )
            
            self.question_repo.add(question)
            
            return {
                "status": "success",
                "message": "Question created successfully",
                "data": self._question_to_dict(question)
            }
        except KeyError as e:
            return {"status": "failed", "message": f"Missing required field: {str(e)}"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_question(self, question_id: UUID, data: dict) -> dict:
        """Cập nhật câu hỏi"""
        try:
            question = self.question_repo.get_by_id(question_id)
            if not question:
                return {"status": "failed", "message": "Question not found"}
            
            # Update fields
            if "level" in data:
                question.level = data["level"]
            if "content_id" in data:
                question.content_id = UUID(data["content_id"])
            if "correct_answer" in data:
                question.correct_answer = data["correct_answer"]
            
            updated_question = self.question_repo.update(question)
            return {
                "status": "success",
                "message": "Question updated successfully",
                "data": self._question_to_dict(updated_question)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_question(self, question_id: UUID) -> dict:
        """Xóa câu hỏi"""
        try:
            success = self.question_repo.delete(question_id)
            if success:
                return {
                    "status": "success",
                    "message": "Question deleted successfully"
                }
            return {"status": "failed", "message": "Question not found"}
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
        try:
            content_id = uuid4() if "content_id" not in data else UUID(data["content_id"])
            
            content = GameContent(
                content_id=content_id,
                game_id=UUID(data["game_id"]),
                level=data["level"],
                content_type=data["content_type"],
                media_path=data.get("media_path"),
                question_text=data.get("question_text"),
                correct_answer=data.get("correct_answer"),
                emotion=data.get("emotion"),
                explanation=data.get("explanation")
            )
            
            self.game_content_repo.add(content)
            
            return {
                "status": "success",
                "message": "Game content created successfully",
                "data": self._content_to_dict(content)
            }
        except KeyError as e:
            return {"status": "failed", "message": f"Missing required field: {str(e)}"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_game_content(self, content_id: UUID, data: dict) -> dict:
        try:
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
            # Update fields
            if "level" in data:
                content.level = data["level"]
            if "content_type" in data:
                content.content_type = data["content_type"]
            if "media_path" in data:
                content.media_path = data["media_path"]
            if "question_text" in data:
                content.question_text = data["question_text"]
            if "correct_answer" in data:
                content.correct_answer = data["correct_answer"]
            if "emotion" in data:
                content.emotion = data["emotion"]
            if "explanation" in data:
                content.explanation = data["explanation"]
            
            updated_content = self.game_content_repo.update(content)
            return {
                "status": "success",
                "message": "Game content updated successfully",
                "data": self._content_to_dict(updated_content)
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def delete_game_content(self, content_id: UUID) -> dict:
        try:
            success = self.game_content_repo.delete(content_id)
            if success:
                return {
                    "status": "success",
                    "message": "Game content deleted successfully"
                }
            return {"status": "failed", "message": "Game content not found"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def _user_to_dict(self, user: User) -> dict:
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "name": user.name
        }

    def _child_to_dict(self, child: Child) -> dict:
        return {
            "user_id": str(child.user_id),
            "age": child.age,
            "last_played": child.last_played.isoformat() if child.last_played else None,
            "report_preferences": child.report_preferences,
            "created_at": child.created_at.isoformat() if child.created_at else None,
            "last_login": child.last_login.isoformat() if child.last_login else None
        }

    def _emotion_to_dict(self, emotion: EmotionConcept) -> dict:
        return {
            "concept_id": str(emotion.concept_id),
            "emotion": emotion.emotion,
            "level": emotion.level,
            "title": emotion.title,
            "video_path": emotion.video_path,
            "image_path": emotion.image_path,
            "audio_path": emotion.audio_path,
            "description": emotion.description
        }

    def _question_to_dict(self, question: Question) -> dict:
        return {
            "question_id": str(question.question_id),
            "game_id": str(question.game_id),
            "level": question.level,
            "content_id": str(question.content_id),
            "correct_answer": question.correct_answer
        }

    def _content_to_dict(self, content: GameContent) -> dict:
        return {
            "content_id": str(content.content_id),
            "game_id": str(content.game_id),
            "level": content.level,
            "content_type": content.content_type,
            "media_path": content.media_path,
            "question_text": content.question_text,
            "correct_answer": content.correct_answer,
            "emotion": content.emotion,
            "explanation": content.explanation
        }