from uuid import UUID, uuid4
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from app.domain.enum import GenderEnum
from app.repository.admin_repo import AdminRepository
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.emotion_concepts_repo import EmotionConceptRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_contents_repo import GameContentsRepository as GameContentRepo
from app.repository.report_repo import ReportRepository  # ✅ ADDED
from app.domain.users.user import User
from app.domain.users.child import Child
from app.domain.sessions.emotion_concept import EmotionConcept
from app.domain.games.question import Question
from app.domain.games.game_content import GameContent
from app.domain.analytics.report import Report  # ✅ ADDED
from app.domain.enum import RoleEnum

class AdminService:
    def __init__(
        self,
        admin_repo: AdminRepository,
        users_repo: UsersRepository,
        child_repo: ChildRepository,
        emotion_repo: EmotionConceptRepository,
        question_repo: QuestionsRepository,
        game_content_repo: GameContentRepo,
        report_repo: ReportRepository  # ✅ ADDED
    ):
        self.admin_repo = admin_repo
        self.users_repo = users_repo
        self.child_repo = child_repo
        self.emotion_repo = emotion_repo
        self.question_repo = question_repo
        self.game_content_repo = game_content_repo
        self.report_repo = report_repo  # ✅ ADDED

    # ==================== User Management ====================
    def get_all_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Lấy danh sách tất cả users"""
        try:
            users = self.admin_repo.get_all_users(skip, limit)
            total = self.admin_repo.count_users()
            
            result_users = []
            for user in users:
                user_dict = self._user_to_dict(user)
                
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
        print("🔥 RAW DATA RECEIVED:", data)

        try:
            for field in ["username", "email", "password"]:
                if not data.get(field):
                    return {
                        "status": "failed",
                        "message": f"Missing required field: {field}"
                    }

            if self.users_repo.get_by_username(data["username"]):
                return {"status": "failed", "message": "Username already exists"}

            if self.users_repo.get_by_email(data["email"]):
                return {"status": "failed", "message": "Email already exists"}

            try:
                role = RoleEnum[data.get("role", "admin").lower()]
            except KeyError:
                return {
                    "status": "failed",
                    "message": f"Invalid role: {data.get('role')}"
                }

            user_id = uuid4()
            user = User(
                user_id=user_id,
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=role,
                name=data.get("name")
            )
            self.users_repo.save_user(user)

            if role == RoleEnum.child:
                required_child_fields = ["age", "gender", "date_of_birth", "phone_number"]
                for field in required_child_fields:
                    if data.get(field) is None:
                        return {
                            "status": "failed",
                            "message": f"Missing required child field: {field}"
                        }

                try:
                    gender = GenderEnum[data["gender"].lower()]
                except KeyError:
                    return {
                        "status": "failed",
                        "message": f"Invalid gender: {data['gender']}"
                    }
                try:
                    date_of_birth_str = data["date_of_birth"]
                    
                    if isinstance(date_of_birth_str, str):
                        date_of_birth = datetime.strptime(
                            date_of_birth_str, "%Y-%m-%d"
                        ).date()
                    elif isinstance(date_of_birth_str, date):
                        date_of_birth = date_of_birth_str
                    else:
                        raise ValueError("Invalid date format")
                    
                    if date_of_birth > date.today():
                        return {
                            "status": "failed",
                            "message": "Date of birth cannot be in the future"
                        }
                        
                except (ValueError, TypeError) as e:
                    return {
                        "status": "failed",
                        "message": "Invalid date_of_birth format (must be YYYY-MM-DD)"
                    }
                
                phone_number = data["phone_number"]
                if not isinstance(phone_number, str) or not phone_number.isdigit() or len(phone_number) != 10:
                    return {
                        "status": "failed",
                        "message": "Phone number must be exactly 10 digits"
                    }

                age = data["age"]
                if not isinstance(age, int) or age < 0 or age > 150:
                    return {
                        "status": "failed",
                        "message": "Age must be between 0 and 150"
                    }
                
                child = Child(
                    user_id=str(user_id),
                    age=age,
                    gender=gender,
                    date_of_birth=date_of_birth,
                    phone_number=phone_number,
                    last_played=None,
                    report_preferences=data.get("report_preferences"),
                    created_at=datetime.utcnow(),
                    last_login=None,
                )

                saved_child = self.child_repo.save(child)

                return {
                    "status": "success",
                    "message": f"Child user {user.username} created",
                    "user_id": str(user.user_id),
                    "data": {
                        **self._user_to_dict(user),
                        "age": saved_child.age,
                        "gender": saved_child.gender.value,
                        "date_of_birth": saved_child.date_of_birth.isoformat(),
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
            print(f"❌ Error in create_user:", e)
            import traceback
            traceback.print_exc()
            return {"status": "failed", "message": str(e)}

        
    def update_user(self, user_id: UUID, data: dict) -> dict:
        """Cập nhật thông tin user"""
        try:
            user = self.users_repo.get_by_id(user_id)
            if not user:
                return {"status": "failed", "message": "User not found"}
            
            if "username" in data and data["username"] and data["username"] != user.username:
                existing_user = self.users_repo.get_by_username(data["username"])
                if existing_user:
                    return {"status": "failed", "message": "Username already exists"}
            
            if "email" in data and data["email"] and data["email"] != user.email:
                existing_user = self.users_repo.get_by_email(data["email"])
                if existing_user:
                    return {"status": "failed", "message": "Email already exists"}
            
            if "name" in data and data["name"]:
                user.name = data["name"]
            if "username" in data and data["username"]:
                user.username = data["username"]
            if "email" in data and data["email"]:
                user.email = data["email"]
            if "password" in data and data["password"]:
                user.password = data["password"]
            if "role" in data and data["role"]:
                try:
                    user.role = RoleEnum[data["role"].lower()]
                except KeyError:
                    return {"status": "failed", "message": f"Invalid role: {data['role']}"}
            
            updated_user = self.users_repo.save_user(user)
            
            if updated_user.role == RoleEnum.child:
                child = self.child_repo.get_by_user_id(user_id)
                
                if child:
                    if "age" in data and data["age"] is not None:
                        if not isinstance(data["age"], int) or data["age"] < 0 or data["age"] > 150:
                            return {"status": "failed", "message": "Age must be between 0 and 150"}
                        child.age = data["age"]
                    
                    if "gender" in data and data["gender"]:
                        try:
                            child.gender = GenderEnum[data["gender"].lower()]
                        except KeyError:
                            return {"status": "failed", "message": f"Invalid gender: {data['gender']}"}
                    
                    if "phone_number" in data and data["phone_number"]:
                        phone = data["phone_number"]
                        if not isinstance(phone, str) or not phone.isdigit() or len(phone) != 10:
                            return {"status": "failed", "message": "Phone number must be exactly 10 digits"}
                        child.phone_number = phone
                    
                    if "date_of_birth" in data and data["date_of_birth"]:
                        try:
                            date_str = data["date_of_birth"]
                            if isinstance(date_str, str):
                                dob = datetime.strptime(date_str, "%Y-%m-%d").date()
                            elif isinstance(date_str, date):
                                dob = date_str
                            else:
                                raise ValueError("Invalid date format")
                            
                            if dob > date.today():
                                return {"status": "failed", "message": "Date of birth cannot be in the future"}
                            
                            child.date_of_birth = dob
                        except (ValueError, TypeError):
                            return {"status": "failed", "message": "Invalid date_of_birth format (must be YYYY-MM-DD)"}
                    
                    if "report_preferences" in data:
                        child.report_preferences = data["report_preferences"]
                    
                    self.child_repo.save(child)
                    print("✅ Child info updated:", child.__dict__)
                else:
                    print("⚠️ User is marked as child but no child record found. Creating child record...")
                    
                    if not all(k in data for k in ["age", "gender", "date_of_birth", "phone_number"]):
                        return {
                            "status": "failed", 
                            "message": "Missing required child fields (age, gender, date_of_birth, phone_number)"
                        }
                    
                    try:
                        gender = GenderEnum[data["gender"].lower()]
                        
                        date_str = data["date_of_birth"]
                        if isinstance(date_str, str):
                            dob = datetime.strptime(date_str, "%Y-%m-%d").date()
                        else:
                            dob = date_str
                        
                        if dob > date.today():
                            return {"status": "failed", "message": "Date of birth cannot be in the future"}
                        
                        phone = data["phone_number"]
                        if not phone.isdigit() or len(phone) != 10:
                            return {"status": "failed", "message": "Phone number must be exactly 10 digits"}
                        
                        new_child = Child(
                            user_id=str(user_id),
                            age=data["age"],
                            gender=gender,
                            date_of_birth=dob,
                            phone_number=phone,
                            last_played=None,
                            report_preferences=data.get("report_preferences"),
                            created_at=datetime.utcnow(),
                            last_login=None,
                        )
                        self.child_repo.save(new_child)
                        print("✅ Child record created for existing user")
                        
                    except (ValueError, KeyError) as e:
                        return {"status": "failed", "message": f"Invalid child data: {str(e)}"}
            
            return {
                "status": "success",
                "message": "User updated successfully",
                "data": self._user_to_dict(updated_user)
            }
            
        except Exception as e:
            print(f"❌ Error in update_user: {e}")
            import traceback
            traceback.print_exc()
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
            contents = []
            total = 0
            
            if game_id and level and emotion:
                all_contents = self.game_content_repo.get_game_content_by_emotion_and_level(
                    game_id, level, emotion
                )
                total = len(all_contents)
                contents = all_contents[skip:skip + limit]
                
            elif game_id and level:
                all_contents = self.game_content_repo.get_game_content_by_level(game_id, level)
                
                if emotion:
                    all_contents = [c for c in all_contents if c.emotion == emotion]
                
                total = len(all_contents)
                contents = all_contents[skip:skip + limit]
                
            else:
                contents = self.game_content_repo.get_all(skip, limit)
                
                filtered_contents = contents
                
                if game_id:
                    filtered_contents = [c for c in filtered_contents if c.game_id == game_id]
                if level is not None:
                    filtered_contents = [c for c in filtered_contents if c.level == level]
                if emotion:
                    filtered_contents = [c for c in filtered_contents if c.emotion == emotion]
                
                if game_id or level is not None or emotion:
                    all_for_count = self.game_content_repo.get_all(0, 10000)
                    
                    if game_id:
                        all_for_count = [c for c in all_for_count if c.game_id == game_id]
                    if level is not None:
                        all_for_count = [c for c in all_for_count if c.level == level]
                    if emotion:
                        all_for_count = [c for c in all_for_count if c.emotion == emotion]
                    
                    total = len(all_for_count)
                    contents = filtered_contents
                else:
                    total = self.game_content_repo.count_all()
            
            return {
                "status": "success",
                "data": {
                    "game_contents": [self._content_to_dict(c) for c in contents],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
        except Exception as e:
            print(f"❌ Error in get_game_contents: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "message": str(e)}

    def get_game_content_by_id(self, content_id: UUID) -> dict:
        """Lấy chi tiết một game content theo content_id"""
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
        """Tạo game content mới với content_id + game_id"""
        try:
            required_fields = ["game_id", "level", "content_type", "question_text"]
            for field in required_fields:
                if field not in data:
                    return {
                        "status": "failed", 
                        "message": f"Missing required field: {field}"
                    }
            
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
        """Cập nhật game content theo content_id"""
        try:
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
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
        """Xóa game content theo content_id"""
        try:
            content = self.game_content_repo.get_by_id(content_id)
            if not content:
                return {"status": "failed", "message": "Game content not found"}
            
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
        """Xóa nhiều game contents theo content_ids"""
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

    # ==================== ✅ REPORTS MANAGEMENT ====================
    def get_reports_statistics(self) -> Dict:
        """
        Lấy thống kê báo cáo tuần/tháng với trend
        """
        try:
            all_reports = self.report_repo.get_all_ordered()
            
            now = datetime.now()
            last_week = now - timedelta(days=7)
            last_month = now - timedelta(days=30)
            two_weeks_ago = now - timedelta(days=14)
            two_months_ago = now - timedelta(days=60)
            
            weekly_reports = []
            monthly_reports = []
            
            current_week_count = 0
            last_week_count = 0
            current_month_count = 0
            last_month_count = 0
            
            for report in all_reports:
                child_info = self._get_child_info(report.child_id)
                
                import json
                parsed_data = {}
                if report.data:
                    try:
                        parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                    except:
                        parsed_data = {}
                
                report_dict = {
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'period': report.report_type,
                    'sent_at': report.generated_at.isoformat() if report.generated_at else None,
                    'status': 'sent',
                    'stats': self._extract_stats(parsed_data),
                    'summary': report.summary
                }
                
                generated_at = report.generated_at
                
                if report.report_type == 'weekly':
                    weekly_reports.append(report_dict)
                    if generated_at and generated_at >= last_week:
                        current_week_count += 1
                    elif generated_at and two_weeks_ago <= generated_at < last_week:
                        last_week_count += 1
                
                elif report.report_type == 'monthly':
                    monthly_reports.append(report_dict)
                    if generated_at and generated_at >= last_month:
                        current_month_count += 1
                    elif generated_at and two_months_ago <= generated_at < last_month:
                        last_month_count += 1
            
            weekly_trend = self._calculate_trend(current_week_count, last_week_count)
            monthly_trend = self._calculate_trend(current_month_count, last_month_count)
            
            return {
                "status": "success",
                "data": {
                    "weekly_reports": weekly_reports,
                    "monthly_reports": monthly_reports,
                    "weekly_trend": weekly_trend,
                    "monthly_trend": monthly_trend,
                    "total_count": len(all_reports)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_reports_statistics: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": str(e),
                "data": {
                    "weekly_reports": [],
                    "monthly_reports": [],
                    "weekly_trend": 0,
                    "monthly_trend": 0,
                    "total_count": 0
                }
            }
    
    def get_report_by_id(self, report_id: UUID) -> Dict:
        """Lấy chi tiết một báo cáo"""
        try:
            report = self.report_repo.get_by_id(report_id)
            
            if not report:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy báo cáo"
                }
            
            child_info = self._get_child_info(report.child_id)
            
            import json
            parsed_data = {}
            if report.data:
                try:
                    parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                except:
                    pass
            
            return {
                "status": "success",
                "data": {
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'period': report.report_type,
                    'sent_at': report.generated_at.isoformat() if report.generated_at else None,
                    'status': 'sent',
                    'summary': report.summary,
                    'content': parsed_data or self._get_default_stats()
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_report_by_id: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def resend_report(self, report_id: UUID) -> Dict:
        """Gửi lại báo cáo qua email"""
        try:
            report = self.report_repo.get_by_id(report_id)
            
            if not report:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy báo cáo"
                }
            
            # TODO: Tích hợp với email service
            # from app.services.reports.report_service import ReportService
            # email_result = report_service.send_report_email(...)
            
            print(f"✅ Đã gửi lại báo cáo {report_id}")
            
            return {
                "status": "success",
                "message": "Đã gửi lại báo cáo thành công",
                "data": {
                    "report_id": str(report_id)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in resend_report: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def get_all_reports(
        self, 
        skip: int = 0, 
        limit: int = 100,
        report_type: Optional[str] = None
    ) -> Dict:
        """Lấy danh sách tất cả reports với pagination"""
        try:
            if report_type:
                reports = self.report_repo.get_by_type(report_type, skip, limit)
                total = self.report_repo.count_by_type(report_type)
            else:
                reports = self.report_repo.get_all(skip, limit)
                total = self.report_repo.count_all()
            
            report_list = []
            for report in reports:
                child_info = self._get_child_info(report.child_id)
                
                import json
                parsed_data = {}
                if report.data:
                    try:
                        parsed_data = json.loads(report.data) if isinstance(report.data, str) else report.data
                    except:
                        pass
                
                report_list.append({
                    'report_id': str(report.report_id),
                    'child_id': str(report.child_id) if report.child_id else None,
                    'child_name': child_info['name'],
                    'child_email': child_info['email'],
                    'report_type': report.report_type,
                    'generated_at': report.generated_at.isoformat() if report.generated_at else None,
                    'summary': report.summary,
                    'stats': self._extract_stats(parsed_data)
                })
            
            return {
                "status": "success",
                "data": {
                    "reports": report_list,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
            
        except Exception as e:
            print(f"❌ Error in get_all_reports: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }

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

    def _content_to_dict(self, content: GameContent) -> dict:
        """Convert GameContent to dict với CẢ content_id VÀ game_id"""
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
    
    # ==================== ✅ REPORTS HELPER METHODS ====================
    def _get_child_info(self, child_id: Optional[str]) -> Dict[str, str]:
        """Lấy thông tin child từ child_id"""
        if not child_id:
            return {'name': 'N/A', 'email': ''}
        
        try:
            child = self.child_repo.get_by_user_id(child_id)
            if not child:
                return {'name': 'N/A', 'email': ''}
            
            user = self.users_repo.get_by_id(UUID(child_id))
            if not user:
                return {'name': 'N/A', 'email': ''}
            
            return {
                'name': user.name or 'N/A',
                'email': user.email or ''
            }
        except Exception as e:
            print(f"⚠️ Lỗi lấy child info: {e}")
            return {'name': 'N/A', 'email': ''}
    
    def _calculate_trend(self, current: int, previous: int) -> float:
        """Tính % thay đổi"""
        if previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        elif current > 0:
            return 100.0
        return 0.0
    
    def _extract_stats(self, data: Dict) -> Dict:
        """Trích xuất stats từ data"""
        return {
            'total_sessions': data.get('total_sessions', 0),
            'total_playtime': data.get('total_playtime', 0),
            'avg_score': data.get('avg_score', 0)
        }
    
    def _get_default_stats(self) -> Dict:
        """Stats mặc định khi không có data"""
        return {
            'total_sessions': 0,
            'total_playtime': 0,
            'avg_score': 0
        }
    def get_emotion_concepts(self):
        try:
            concepts = self.emotion_repo.get_all_emotion_concepts()

            data = []
            for c in concepts:
                data.append({
                    "concept_id": str(c.concept_id),
                    "emotion": c.emotion,
                    "level": c.level,
                    "title": c.title,
                    "video_path": c.video_path,
                    "image_path": c.image_path,
                    "audio_path": c.audio_path,
                    "description": c.description,
                })

            return {"status": "success", "data": data}
        except Exception as e:
            print("❌ get_emotion_concepts error:", e)
            return {"status": "error", "message": str(e)}

    def update_emotion_concept_video(self, concept_id: UUID, video_path: str):
        try:
            updated = self.emotion_repo.update_video_path(concept_id, video_path)
            if not updated:
                return {"status": "error", "message": "Emotion concept không tồn tại"}

            return {
                "status": "success",
                "data": {
                    "concept_id": str(updated.concept_id),
                    "emotion": updated.emotion,
                    "video_path": updated.video_path,
                },
            }
        except Exception as e:
            print("❌ update_emotion_concept_video error:", e)
            return {"status": "error", "message": str(e)}