from uuid import UUID, uuid4
from typing import List, Dict, Optional
from app.repository.admin_repo import AdminRepository
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
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
        users_repo: UsersRepository,
        child_repo: ChildRepository,
        emotion_repo: EmotionConceptRepository,
        question_repo: QuestionsRepository,
        game_content_repo: GameContentRepo
    ):
        self.admin_repo = admin_repo
        self.users_repo = users_repo
        self.child_repo = child_repo
        self.emotion_repo = emotion_repo
        self.question_repo = question_repo
        self.game_content_repo = game_content_repo

    # ==================== User Management ====================
    def get_all_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Lấy danh sách tất cả users"""
        try:
            users = self.admin_repo.get_all_users(skip, limit)
            total = self.admin_repo.count_users()
            
            # Kết hợp thông tin user + child
            result_users = []
            for user in users:
                user_dict = self._user_to_dict(user)
                
                # Lấy thông tin child nếu có
                child = self.child_repo.get_by_user_id(user.user_id)
                if child:
                    user_dict['age'] = child.age
                    user_dict['gender'] = child.gender.value if child.gender else None
                    user_dict['created_at'] = child.created_at.isoformat() if child.created_at else None
                else:
                    user_dict['age'] = None
                    user_dict['gender'] = None
                    user_dict['created_at'] = None
                
                result_users.append(user_dict)
            
            return {
                "status": "success",
                "data": {
                    "users": result_users,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            print(f"❌ Error in get_all_users: {e}")
            return {"status": "failed", "message": str(e)}

    def get_user_by_id(self, user_id: UUID) -> dict:
        """Lấy thông tin chi tiết user"""
        try:
            user = self.users_repo.get_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            
            user_dict = self._user_to_dict(user)
            
            # Lấy thông tin child nếu có
            child = self.child_repo.get_by_user_id(user_id)
            if child:
                user_dict['age'] = child.age
                user_dict['gender'] = child.gender.value if child.gender else None
                user_dict['phone_number'] = child.phone_number
                user_dict['created_at'] = child.created_at.isoformat() if child.created_at else None
            
            return {
                "status": "success",
                "data": user_dict
            }
        except Exception as e:
            print(f"❌ Error in get_user_by_id: {e}")
            return {"status": "failed", "message": str(e)}

    def create_user(self, data: dict) -> dict:
        """Tạo user mới (bởi admin)"""
        try:
            # Validate required fields
            required_fields = ["username", "email", "password"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return {
                        "status": "failed", 
                        "message": f"Missing required field: {field}"
                    }
            
            # Kiểm tra username đã tồn tại
            existing_user_by_username = self.users_repo.get_by_username(data.get("username"))
            if existing_user_by_username:
                return {"status": "failed", "message": "Username already exists"}

            # Kiểm tra email đã tồn tại
            existing_user_by_email = self.users_repo.get_by_email(data.get("email"))
            if existing_user_by_email:
                return {"status": "failed", "message": "Email already exists"}

            # Xác định role
            role = RoleEnum.admin  # default role
            if "role" in data and data["role"]:
                try:
                    role = RoleEnum[data["role"].upper()]
                except KeyError:
                    return {"status": "failed", "message": f"Invalid role: {data['role']}"}

            # Tạo user
            user_id = uuid4()
            user = User(
                user_id=user_id,
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password"),
                role=role,
                name=data.get("name")
            )

            self.users_repo.save(user)
            
            # Nếu role là child, tạo thêm child record
            if role == RoleEnum.child:
                from app.domain.enum import GenderEnum
                from datetime import datetime
                
                # Parse gender nếu có
                gender = None
                if "gender" in data and data["gender"]:
                    try:
                        gender = GenderEnum[data["gender"].upper()]
                    except KeyError:
                        # Nếu gender không hợp lệ, bỏ qua hoặc trả về lỗi
                        pass
                
                child = Child(
                    user_id=str(user_id),
                    age=data.get("age"),
                    last_played=None,
                    report_preferences=data.get("report_preferences"),
                    created_at=datetime.utcnow(),
                    last_login=None,
                    gender=gender,
                    date_of_birth=data.get("date_of_birth"),
                    phone_number=data.get("phone_number")
                )
                
                saved_child = self.child_repo.save(child)
                print("✅ Child created by admin:", saved_child.__dict__)
                
                return {
                    "status": "success", 
                    "message": f"Child user {user.username} created",
                    "user_id": str(user.user_id),
                    "data": {
                        **self._user_to_dict(user),
                        "age": saved_child.age,
                        "gender": saved_child.gender.value if saved_child.gender else None,
                        "phone_number": saved_child.phone_number
                    }
                }
            
            return {
                "status": "success", 
                "message": f"User {user.username} created",
                "user_id": str(user.user_id),
                "data": self._user_to_dict(user)
            }
            
        except Exception as e:
            print(f"❌ Error in create_user: {e}")
            return {"status": "failed", "message": str(e)}
    
    def update_user(self, user_id: UUID, data: dict) -> dict:
        """Cập nhật thông tin user"""
        try:
            user = self.users_repo.get_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            
            # Kiểm tra username đã tồn tại (nếu đang update username)
            if "username" in data and data["username"] and data["username"] != user.username:
                existing_user = self.users_repo.get_by_username(data["username"])
                if existing_user:
                    return {"status": "failed", "message": "Username already exists"}
            
            # Kiểm tra email đã tồn tại (nếu đang update email)
            if "email" in data and data["email"] and data["email"] != user.email:
                existing_user = self.users_repo.get_by_email(data["email"])
                if existing_user:
                    return {"status": "failed", "message": "Email already exists"}
            
            # Update user fields
            if "name" in data and data["name"]:
                user.name = data["name"]
            if "username" in data and data["username"]:
                user.username = data["username"]
            if "email" in data and data["email"]:
                user.email = data["email"]
            if "password" in data and data["password"]:
                user.password = data["password"]
            if "role" in data and data["role"]:
                # Convert string role to RoleEnum
                try:
                    user.role = RoleEnum[data["role"].upper()]
                except KeyError:
                    return {"status": "failed", "message": f"Invalid role: {data['role']}"}
            
            # Lưu user
            updated_user = self.users_repo.save_user(user)
            
            # Update child info nếu là child và có data liên quan
            if updated_user.role == RoleEnum.child:
                child = self.child_repo.get_by_user_id(user_id)
                if child:
                    child_fields = ["age", "gender", "phone_number", "report_preferences"]
                    child_data = {k: v for k, v in data.items() if k in child_fields and v is not None}
                    
                    if child_data:
                        for key, value in child_data.items():
                            if key == "gender":
                                from app.domain.enum import GenderEnum
                                try:
                                    setattr(child, key, GenderEnum[value.upper()])
                                except KeyError:
                                    return {"status": "failed", "message": f"Invalid gender: {value}"}
                            else:
                                setattr(child, key, value)
                        
                        self.child_repo.save(child)
                        print("✅ Child info updated:", child.__dict__)
            
            return {
                "status": "success",
                "message": "User updated successfully",
                "data": self._user_to_dict(updated_user)
            }
        except Exception as e:
            print(f"❌ Error in update_user: {e}")
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
            print(f"❌ Error in delete_user: {e}")
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
            print(f"❌ Error in get_all_children: {e}")
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
            print(f"❌ Error in search_users: {e}")
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
                concept_id=data.get("concept_id") or uuid4(),
                emotion=data.get("emotion"),
                level=data.get("level"),
                title=data.get("title"),
                video_path=data.get("video_path"),
                image_path=data.get("image_path"),
                audio_path=data.get("audio_path"),
                description=data.get("description")
            )
            saved_emotion = self.emotion_repo.create(emotion)
            
            return {
                "status": "success",
                "message": "Emotion concept created successfully",
                "data": self._emotion_to_dict(saved_emotion)
            }
        except Exception as e:
            print(f"❌ Error in create_emotion_concept: {e}")
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
            question = Question(
                question_id=data.get("question_id") or uuid4(),
                game_id=data["game_id"],
                level=data["level"],
                content_id=data["content_id"],
                correct_answer=data.get("correct_answer")
            )
            saved_question = self.question_repo.create(question)
            
            return {
                "status": "success",
                "message": "Question created successfully",
                "data": self._question_to_dict(saved_question)
            }
        except Exception as e:
            print(f"❌ Error in create_question: {e}")
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
                question.content_id = data["content_id"]
            if "correct_answer" in data:
                question.correct_answer = data["correct_answer"]
            
            updated_question = self.question_repo.save(question)
            
            return {
                "status": "success",
                "message": "Question updated successfully",
                "data": self._question_to_dict(updated_question)
            }
        except Exception as e:
            print(f"❌ Error in update_question: {e}")
            return {"status": "failed", "message": str(e)}

    def delete_question(self, question_id: UUID) -> dict:
        """Xóa câu hỏi"""
        try:
            question = self.question_repo.get_by_id(question_id)
            if not question:
                return {"status": "failed", "message": "Question not found"}
            
            success = self.question_repo.delete(question_id)
            
            if success:
                return {
                    "status": "success",
                    "message": "Question deleted successfully"
                }
            return {"status": "failed", "message": "Failed to delete question"}
        except Exception as e:
            print(f"❌ Error in delete_question: {e}")
            return {"status": "failed", "message": str(e)}

    # ==================== Game Content Management ====================
    def get_game_contents(
        self, 
        game_id: Optional[UUID] = None, 
        level: Optional[int] = None, 
        emotion: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """Lấy danh sách game contents với filter"""
        try:
            # Case 1: Filter đầy đủ theo game_id, level và emotion
            if game_id and level and emotion:
                contents = self.game_content_repo.get_game_content_by_emotion_and_level(
                    game_id, level, emotion
                )
                total = len(contents)
                contents = contents[skip:skip + limit]
            
            # Case 2: Filter theo game_id và level
            elif game_id and level:
                contents = self.game_content_repo.get_game_content_by_level(game_id, level)
                
                # Filter thêm theo emotion nếu có
                if emotion:
                    contents = [c for c in contents if c.emotion == emotion]
                
                total = len(contents)
                contents = contents[skip:skip + limit]
            
            # Case 3: Lấy tất cả với pagination
            else:
                contents = self.game_content_repo.get_all(skip, limit)
                
                # Apply filters nếu có
                if game_id:
                    contents = [c for c in contents if c.game_id == game_id]
                if level is not None:
                    contents = [c for c in contents if c.level == level]
                if emotion:
                    contents = [c for c in contents if c.emotion == emotion]
                
                total = len(contents)
            
            return {
                "status": "success",
                "data": {
                    "contents": [self._content_to_dict(c) for c in contents],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            print(f"❌ Error in get_game_contents: {e}")
            return {"status": "failed", "message": str(e)}

    def get_game_content_by_id(self, content_id: UUID) -> dict:
        """Lấy chi tiết một game content"""
        try:
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
            return {
                "status": "success",
                "data": self._content_to_dict(content)
            }
        except Exception as e:
            print(f"❌ Error in get_game_content_by_id: {e}")
            return {"status": "failed", "message": str(e)}

    def create_game_content(self, data: dict) -> dict:
        """Tạo game content mới"""
        try:
            # Validate required fields
            required_fields = ["game_id", "level", "content_type", "question_text"]
            for field in required_fields:
                if field not in data:
                    return {
                        "status": "failed", 
                        "message": f"Missing required field: {field}"
                    }
            
            # Tạo GameContent domain entity
            content = GameContent(
                content_id=uuid4(),
                game_id=data["game_id"],
                level=data["level"],
                content_type=data["content_type"],
                media_path=data.get("media_path"),
                question_text=data["question_text"],
                correct_answer=data.get("correct_answer"),
                emotion=data.get("emotion"),
                explanation=data.get("explanation")
            )
            
            # Lưu vào database
            saved_content = self.game_content_repo.create(content)
            
            return {
                "status": "success",
                "message": "Game content created successfully",
                "data": self._content_to_dict(saved_content)
            }
        except Exception as e:
            print(f"❌ Error in create_game_content: {e}")
            return {"status": "failed", "message": str(e)}

    def update_game_content(self, content_id: UUID, data: dict) -> dict:
        """Cập nhật game content"""
        try:
            # Lấy content hiện tại
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
            # Cập nhật các field nếu có trong data
            if "level" in data and data["level"] is not None:
                content.level = data["level"]
            if "content_type" in data and data["content_type"]:
                content.content_type = data["content_type"]
            if "media_path" in data:
                content.media_path = data["media_path"]
            if "question_text" in data and data["question_text"]:
                content.question_text = data["question_text"]
            if "correct_answer" in data:
                content.correct_answer = data["correct_answer"]
            if "emotion" in data:
                content.emotion = data["emotion"]
            if "explanation" in data:
                content.explanation = data["explanation"]
            
            # Lưu cập nhật
            updated_content = self.game_content_repo.save(content)
            
            return {
                "status": "success",
                "message": "Game content updated successfully",
                "data": self._content_to_dict(updated_content)
            }
        except Exception as e:
            print(f"❌ Error in update_game_content: {e}")
            return {"status": "failed", "message": str(e)}

    def delete_game_content(self, content_id: UUID) -> dict:
        """Xóa game content"""
        try:
            # Kiểm tra content có tồn tại không
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
            # Xóa content
            success = self.game_content_repo.delete(content_id)
            
            if success:
                return {
                    "status": "success",
                    "message": "Game content deleted successfully"
                }
            return {"status": "failed", "message": "Failed to delete game content"}
        except Exception as e:
            print(f"❌ Error in delete_game_content: {e}")
            return {"status": "failed", "message": str(e)}

    def bulk_delete_game_contents(self, content_ids: List[UUID]) -> dict:
        """Xóa nhiều game contents cùng lúc"""
        try:
            if not content_ids:
                return {
                    "status": "failed",
                    "message": "No content IDs provided"
                }
            
            deleted_count = 0
            failed_ids = []
            
            for content_id in content_ids:
                try:
                    success = self.game_content_repo.delete(content_id)
                    if success:
                        deleted_count += 1
                    else:
                        failed_ids.append(str(content_id))
                except Exception as e:
                    print(f"❌ Failed to delete {content_id}: {e}")
                    failed_ids.append(str(content_id))
            
            message = f"Deleted {deleted_count}/{len(content_ids)} game contents"
            if failed_ids:
                message += f". Failed IDs: {', '.join(failed_ids[:5])}"
                if len(failed_ids) > 5:
                    message += f" and {len(failed_ids) - 5} more"
            
            return {
                "status": "success" if deleted_count > 0 else "failed",
                "message": message,
                "data": {
                    "deleted": deleted_count,
                    "total": len(content_ids),
                    "failed_count": len(failed_ids),
                    "failed_ids": failed_ids
                }
            }
        except Exception as e:
            print(f"❌ Error in bulk_delete_game_contents: {e}")
            return {"status": "failed", "message": str(e)}

    # ==================== Helper Methods ====================
    def _user_to_dict(self, user: User) -> dict:
        """Convert User domain entity to dict"""
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "name": user.name
        }

    def _child_to_dict(self, child: Child) -> dict:
        """Convert Child domain entity to dict"""
        return {
            "user_id": str(child.user_id),
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
            "title": emotion.title,
            "video_path": emotion.video_path,
            "image_path": emotion.image_path,
            "audio_path": emotion.audio_path,
            "description": emotion.description
        }

    def _question_to_dict(self, question: Question) -> dict:
        """Convert Question to dict"""
        return {
            "question_id": str(question.question_id),
            "game_id": str(question.game_id),
            "level": question.level,
            "content_id": str(question.content_id),
            "correct_answer": question.correct_answer
        }

    def _content_to_dict(self, content: GameContent) -> dict:
        """Convert GameContent to dict"""
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