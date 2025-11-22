from uuid import UUID, uuid4
from typing import List, Optional
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.sessions_repo import SessionsRepository
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.domain.sessions.session import Session
from app.domain.enum import SessionStateEnum
from datetime import datetime


class CVService:
    def __init__(self, games_repo: GamesRepository, 
                 game_contents_repo: GameContentsRepository,
                 sessions_repo: SessionsRepository,
                 session_questions_repo: SessionQuestionsRepository):
        self.games_repo = games_repo
        self.game_contents_repo = game_contents_repo
        self.sessions_repo = sessions_repo
        self.session_questions_repo = session_questions_repo

    def get_scenarios(self) -> List[dict]:
        """Lấy danh sách 6 tình huống cho game CV từ database."""
        try:
            # Tìm game CV
            games = self.games_repo.get_all()
            cv_game = next((g for g in games if g.game_type == "GameCV"), None)
            
            if not cv_game:
                # Nếu chưa có game CV, trả về default scenarios
                print("GameCV not found in database, returning default scenarios")
                return self._get_default_scenarios()
            
            # Lấy game contents (scenarios) cho game CV
            contents = self.game_contents_repo.get_by_game_id(cv_game.game_id)
            
            if not contents:
                # Nếu chưa có scenarios trong DB, trả về default
                print(f"GameCV found but no scenarios in DB (game_id: {cv_game.game_id}), returning default scenarios")
                return self._get_default_scenarios()
            
            # Map to scenario format từ database
            scenarios = []
            for content in contents:
                try:
                    # question_text = title
                    # explanation = description
                    # media_path = image_path
                    # emotion = target_emotion
                    title = content.question_text or "Tình huống"
                    description = content.explanation or ""
                    image_path = content.media_path or ""
                    target_emotion = content.emotion or ""
                    
                    # Lấy hint từ hàm helper (có thể lưu trong DB sau)
                    hint = self._get_hint(target_emotion, description)
                    
                    scenarios.append({
                        "id": str(content.content_id),
                        "title": title,
                        "description": description,
                        "target_emotion": target_emotion,
                        "instruction": self._get_instruction(target_emotion),
                        "hint": hint,
                        "image_path": image_path,
                        "explanation": self._get_explanation(target_emotion),
                        "level": content.level if hasattr(content, 'level') and content.level else 1
                    })
                except Exception as e:
                    print(f"Error processing content {content.content_id if hasattr(content, 'content_id') else 'unknown'}: {str(e)}")
                    continue
            
            # Sắp xếp theo thứ tự: vui, ngạc nhiên, buồn, tức giận, sợ hãi, ghê tởm
            emotion_order = ["vui", "ngạc nhiên", "buồn", "tức giận", "sợ hãi", "ghê tởm"]
            scenarios.sort(key=lambda x: emotion_order.index(x["target_emotion"]) if x["target_emotion"] in emotion_order else 999)
            
            print(f"Successfully loaded {len(scenarios)} scenarios from database")
            return scenarios
        except Exception as e:
            import traceback
            print(f"Error in get_scenarios: {str(e)}")
            print(traceback.format_exc())
            # Trả về default scenarios nếu có lỗi
            print("Returning default scenarios due to error")
            return self._get_default_scenarios()
    
    def _get_hint(self, emotion: str, description: str = "") -> str:
        """Lấy hint theo cảm xúc."""
        hints = {
            "vui": "Hãy tưởng tượng con vừa nhận được món quà yêu thích!",
            "ngạc nhiên": "Hãy tưởng tượng một điều gì đó bất ngờ xảy ra!",
            "buồn": "Hãy tưởng tượng món đồ yêu thích của con bị hỏng.",
            "tức giận": "Hãy tưởng tượng ai đó lấy mất đồ của con mà không hỏi.",
            "sợ hãi": "Hãy tưởng tượng một âm thanh lớn và đáng sợ.",
            "ghê tởm": "Hãy tưởng tượng mùi hôi khó chịu."
        }
        return hints.get(emotion, "Hãy tưởng tượng tình huống này!")
    
    def _get_explanation(self, emotion: str) -> str:
        """Lấy giải thích về cảm xúc."""
        explanations = {
            "vui": "Khi nhận được quà bất ngờ, chúng ta thường cảm thấy vui vẻ và hạnh phúc.",
            "ngạc nhiên": "Khi gặp điều bất ngờ, chúng ta thường mở to mắt và há miệng.",
            "buồn": "Khi mất mát thứ gì đó quan trọng, chúng ta cảm thấy buồn.",
            "tức giận": "Khi bị đối xử không công bằng, chúng ta có thể cảm thấy tức giận.",
            "sợ hãi": "Khi gặp điều đáng sợ, chúng ta thường cảm thấy lo lắng và sợ hãi.",
            "ghê tởm": "Khi gặp thứ gì đó khó chịu, chúng ta thường nhăn mặt và cảm thấy ghê tởm."
        }
        return explanations.get(emotion, "")

    def _get_instruction(self, emotion: str) -> str:
        """Lấy lời hướng dẫn theo cảm xúc."""
        instructions = {
            "vui": "Con thử cười tự nhiên nhé.",
            "ngạc nhiên": "Mắt mở to, miệng hé nhẹ.",
            "buồn": "Mắt rũ xuống, môi dưới hơi trễ.",
            "tức giận": "Lông mày hạ xuống, ánh mắt nghiêm.",
            "sợ hãi": "Mắt mở to, hơi khép vai.",
            "ghê tởm": "Mũi nhăn, miệng hơi mở, lông mày cau lại."
        }
        return instructions.get(emotion, "Con thể hiện cảm xúc này nhé.")

    def _get_default_scenarios(self) -> List[dict]:
        """Trả về 6 tình huống mặc định nếu chưa có trong database."""
        return [
            {
                "id": str(uuid4()),
                "title": "Quà bất ngờ",
                "description": "Con mở hộp quà bất ngờ và thấy món con thích.",
                "target_emotion": "vui",
                "instruction": "Con thử cười tự nhiên nhé.",
                "hint": "Hãy tưởng tượng con vừa nhận được món quà yêu thích!",
                "image_path": "/assets/images/happy/situation_happy.png",
                "explanation": "Khi nhận được quà bất ngờ, chúng ta thường cảm thấy vui vẻ và hạnh phúc.",
                "level": 1
            },
            {
                "id": str(uuid4()),
                "title": "Bất ngờ lớn",
                "description": "Một quả bóng bỗng nổ to bên cạnh con.",
                "target_emotion": "ngạc nhiên",
                "instruction": "Mắt mở to, miệng hé nhẹ.",
                "hint": "Hãy tưởng tượng một điều gì đó bất ngờ xảy ra!",
                "image_path": "/assets/images/surprise/situation_surprise.png",
                "explanation": "Khi gặp điều bất ngờ, chúng ta thường mở to mắt và há miệng.",
                "level": 1
            },
            {
                "id": str(uuid4()),
                "title": "Món đồ yêu thích bị vỡ",
                "description": "Đồ chơi con thích bị rơi và vỡ.",
                "target_emotion": "buồn",
                "instruction": "Mắt rũ xuống, môi dưới hơi trễ.",
                "hint": "Hãy tưởng tượng món đồ yêu thích của con bị hỏng.",
                "image_path": "/assets/images/sad/situation_sad.png",
                "explanation": "Khi mất mát thứ gì đó quan trọng, chúng ta cảm thấy buồn.",
                "level": 1
            },
            {
                "id": str(uuid4()),
                "title": "Bạn lấy đồ",
                "description": "Bạn cầm mất món đồ con đang chơi.",
                "target_emotion": "tức giận",
                "instruction": "Lông mày hạ xuống, ánh mắt nghiêm.",
                "hint": "Hãy tưởng tượng ai đó lấy mất đồ của con mà không hỏi.",
                "image_path": "/assets/images/angry/situation_angry.png",
                "explanation": "Khi bị đối xử không công bằng, chúng ta có thể cảm thấy tức giận.",
                "level": 1
            },
            {
                "id": str(uuid4()),
                "title": "Tiếng sấm đêm",
                "description": "Tiếng sấm rất to lúc trời tối.",
                "target_emotion": "sợ hãi",
                "instruction": "Mắt mở to, hơi khép vai.",
                "hint": "Hãy tưởng tượng một âm thanh lớn và đáng sợ.",
                "image_path": "/assets/images/fear/situation_fear.png",
                "explanation": "Khi gặp điều đáng sợ, chúng ta thường cảm thấy lo lắng và sợ hãi.",
                "level": 1
            },
            {
                "id": str(uuid4()),
                "title": "Món ăn hư",
                "description": "Con ngửi thấy món ăn đã bị hư.",
                "target_emotion": "ghê tởm",
                "instruction": "Mũi nhăn, miệng hơi mở, lông mày cau lại.",
                "hint": "Hãy tưởng tượng mùi hôi khó chịu.",
                "image_path": "/assets/images/disgust/situation_disgust.png",
                "explanation": "Khi gặp thứ gì đó khó chịu, chúng ta thường nhăn mặt và cảm thấy ghê tởm.",
                "level": 1
            }
        ]

    def start_session(self, user_id: str, game_type: str) -> dict:
        """Khởi tạo session cho game CV."""
        # Tìm game CV
        games = self.games_repo.get_all()
        cv_game = next((g for g in games if g.game_type == "GameCV"), None)
        
        if not cv_game:
            # Tạo game CV nếu chưa có
            from app.domain.games.game import GameCV
            cv_game = GameCV(
                game_id=uuid4(),
                game_type="GameCV",
                name="Game CV - Nhận diện cảm xúc",
                level=1,
                difficulty_level=1,
                max_errors=3,
                level_threshold=5,
                time_limit=300,
                cv_model={},
                camera_stream={}
            )
            cv_game = self.games_repo.save(cv_game)
        
        # Tạo session using the repository's start_session method
        try:
            saved_session = self.sessions_repo.start_session(UUID(user_id), cv_game.game_id)
            return {
                "session_id": str(saved_session.session_id),
                "message": "Session started successfully"
            }
        except Exception as e:
            print(f"Error using start_session method: {e}")
            # Fallback: create session manually using model directly
            from app.models.sessions.session import Session as SessionModel, SessionStateEnum as ModelSessionStateEnum
            
            session_model = SessionModel(
                session_id=uuid4(),
                user_id=UUID(user_id),
                game_id=cv_game.game_id,
                start_time=datetime.utcnow(),
                state=ModelSessionStateEnum.playing,
                score=0,
                emotion_errors={},
                max_errors=3,
                level_threshold=100,
                ratio=[],
                time_limit=300,
                question_ids=[]
            )
            
            self.sessions_repo.db_session.add(session_model)
            self.sessions_repo.db_session.commit()
            self.sessions_repo.db_session.refresh(session_model)
            
            return {
                "session_id": str(session_model.session_id),
                "message": "Session started successfully"
            }

    def save_result(self, session_id: UUID, scenario_id: UUID, 
                   target_emotion: str, detected_emotion: Optional[str],
                   success: bool, time_taken: int) -> dict:
        """Lưu kết quả của một bài."""
        # Lấy session - need to check the actual structure
        try:
            # Try to get session by session_id
            session_model = self.sessions_repo.db_session.query(
                self.sessions_repo.model_class
            ).filter(
                self.sessions_repo.model_class.session_id == session_id
            ).first()
            
            if not session_model:
                return {"status": "error", "message": "Session not found"}
            
            # Update session score
            if success:
                session_model.score = (session_model.score or 0) + 10
            
            # Update emotion errors
            if session_model.emotion_errors:
                emotion_errors = dict(session_model.emotion_errors) if isinstance(session_model.emotion_errors, dict) else {}
            else:
                emotion_errors = {}
            
            if target_emotion not in emotion_errors:
                emotion_errors[target_emotion] = {"correct": 0, "incorrect": 0}
            elif not isinstance(emotion_errors[target_emotion], dict):
                emotion_errors[target_emotion] = {"correct": 0, "incorrect": 0}
            
            if success:
                emotion_errors[target_emotion]["correct"] = emotion_errors[target_emotion].get("correct", 0) + 1
            else:
                emotion_errors[target_emotion]["incorrect"] = emotion_errors[target_emotion].get("incorrect", 0) + 1
            
            session_model.emotion_errors = emotion_errors
            self.sessions_repo.db_session.commit()
            
            return {
                "status": "success",
                "message": "Result saved successfully"
            }
        except Exception as e:
            return {"status": "error", "message": f"Error saving result: {str(e)}"}

