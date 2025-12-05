from uuid import UUID, uuid4
import json
from typing import List, Optional
from app.repository.games_repo import GamesRepository
from app.repository.game_contents_repo import GameContentsRepository
from app.repository.sessions_repo import SessionsRepository
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.repository.questions_repo import QuestionsRepository
from app.repository.game_history_repo import GameHistoryRepository
from app.repository.session_history_repo import SessionHistoryRepository
from app.repository.child_progress_repo import ChildProgressRepository
from app.domain.sessions.session import Session
from app.domain.enum import SessionStateEnum
from app.domain.sessions.session_questions import SessionQuestions
from app.domain.analytics.game_history import GameHistory
from app.domain.analytics.session_history import SessionHistory
from app.domain.analytics.child_progress import ChildProgress
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
        # Initialize additional repositories from db_session
        self.questions_repo = QuestionsRepository(sessions_repo.db_session)
        self.game_history_repo = GameHistoryRepository(sessions_repo.db_session)
        self.session_history_repo = SessionHistoryRepository(sessions_repo.db_session)
        self.child_progress_repo = ChildProgressRepository(sessions_repo.db_session)

    def get_scenarios(self, level: int = 1) -> List[dict]:
        """Lấy danh sách scenarios cho game CV từ database, random 10 màn cho mỗi level."""
        try:
            import random
            
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
            
            # Map to scenario format từ database và filter theo level
            scenarios = []
            for content in contents:
                try:
                    content_level = content.level if hasattr(content, 'level') and content.level else 1
                    # Chỉ lấy scenarios của level được yêu cầu
                    if content_level != level:
                        continue
                    
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
                        "level": content_level
                    })
                except Exception as e:
                    print(f"Error processing content {content.content_id if hasattr(content, 'content_id') else 'unknown'}: {str(e)}")
                    continue
            
            print(f"Found {len(scenarios)} scenarios for level {level}")
            
            # Random 10 scenarios (hoặc tất cả nếu ít hơn 10)
            if len(scenarios) > 10:
                scenarios = random.sample(scenarios, 10)
                print(f"Randomly selected 10 scenarios from available scenarios")
            elif len(scenarios) == 0:
                print(f"⚠️ No scenarios found for level {level}, returning default scenarios")
                return self._get_default_scenarios()
            else:
                print(f"Using all {len(scenarios)} scenarios (less than 10 available)")
            
            # Shuffle để random thứ tự
            random.shuffle(scenarios)
            
            print(f"Successfully loaded {len(scenarios)} scenarios for level {level}")
            return scenarios
        except Exception as e:
            import traceback
            print(f"Error in get_scenarios: {str(e)}")
            print(traceback.format_exc())
            # Trả về default scenarios nếu có lỗi
            print("Returning default scenarios due to error")
            return self._get_default_scenarios()
    
    def get_requests(self) -> List[dict]:
        """Lấy danh sách yêu cầu biểu cảm (không kịch bản) cho game CV."""
        try:
            games = self.games_repo.get_all()
            # Ưu tiên game có type riêng, fallback về GameCV nếu chưa tách
            request_game = next(
                (
                    g
                    for g in games
                    if getattr(g, "game_type", "") in {"GameCVRequest", "GameCV_Request", "GameCV"}  # type: ignore[attr-defined]
                ),
                None,
            )

            if not request_game:
                print("GameCVRequest not found in database, returning default requests")
                return self._get_default_requests()

            contents = self.game_contents_repo.get_by_game_id(request_game.game_id)

            if not contents:
                print(
                    f"GameCVRequest found but no contents in DB (game_id: {request_game.game_id}), returning default requests"
                )
                return self._get_default_requests()

            requests: List[dict] = []
            for content in contents:
                try:
                    target_emotion = content.emotion or ""
                    description = content.explanation or self._build_request_description(target_emotion)

                    requests.append(
                        {
                            "id": str(content.content_id),
                            "title": content.question_text or "Thử thách biểu cảm",
                            "description": description,
                            "target_emotion": target_emotion,
                            "instruction": self._get_instruction(target_emotion),
                            "hint": self._get_hint(target_emotion),
                            "image_path": content.media_path or "",
                            "explanation": description,
                            "level": content.level if hasattr(content, "level") and content.level else 1,
                        }
                    )
                except Exception as e:  # pragma: no cover - phòng lỗi dữ liệu
                    print(
                        f"Error processing request content {content.content_id if hasattr(content, 'content_id') else 'unknown'}: {str(e)}"
                    )
                    continue

            # Nếu dữ liệu DB hợp lệ, trả về theo thứ tự cảm xúc quen thuộc
            emotion_order = ["vui", "ngạc nhiên", "buồn", "tức giận", "sợ hãi", "ghê tởm"]
            requests.sort(
                key=lambda x: emotion_order.index(x["target_emotion"]) if x["target_emotion"] in emotion_order else 999
            )

            if not requests:
                print("No valid request contents found, returning default requests")
                return self._get_default_requests()

            print(f"Successfully loaded {len(requests)} request prompts from database")
            return requests
        except Exception as e:  # pragma: no cover - phòng lỗi không mong muốn
            import traceback
            print(f"Error in get_requests: {str(e)}")
            print(traceback.format_exc())
            print("Returning default requests due to error")
            return self._get_default_requests()

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

    def get_level_threshold(self, level: int) -> float:
        """
        Lấy ngưỡng confidence (%) cho mỗi level.
        Bé cần giữ confidence >= threshold trong >= 1s để pass màn.
        """
        thresholds = {
            1: 40.0,
            2: 50.0,
            3: 60.0,
            4: 70.0,
            5: 80.0,
            6: 90.0
        }
        return thresholds.get(level, 40.0)  # Default 40% nếu level không hợp lệ
    
    def get_max_level(self) -> int:
        """Số level tối đa của game CV tình huống."""
        return 6
    
    def _normalize_emotion_name(self, emotion: str) -> str:
        """Normalize tên cảm xúc về tên chuẩn (6 cảm xúc chuẩn)."""
        if not emotion:
            return ""
        
        emotion_clean = emotion.strip()
        emotion_lower = emotion_clean.lower()
        
        # Map tất cả các biến thể tên cảm xúc về tên chuẩn (bao gồm cả encoding sai)
        emotion_name_mapping = {
            "vui": "vui",
            "vui vẻ": "vui",
            "vui ve": "vui",
            "happy": "vui",
            "buồn": "buồn",
            "buồn bã": "buồn",
            "buon": "buồn",
            "buon ba": "buồn",
            "bu?n": "buồn",  # Encoding sai
            "bu?n bã": "buồn",  # Encoding sai
            "sad": "buồn",
            "ngạc nhiên": "ngạc nhiên",
            "ng?c nhiên": "ngạc nhiên",  # Encoding sai
            "ng?c nhi?n": "ngạc nhiên",  # Encoding sai
            "ngac nhien": "ngạc nhiên",
            "surprise": "ngạc nhiên",
            "tức giận": "tức giận",
            "t?c gi?n": "tức giận",  # Encoding sai - FIX
            "tức": "tức giận",
            "tuc gian": "tức giận",
            "tuc": "tức giận",
            "angry": "tức giận",
            "sợ hãi": "sợ hãi",
            "s? hãi": "sợ hãi",  # Encoding sai
            "s?": "sợ hãi",  # Encoding sai
            "sợ": "sợ hãi",
            "so hai": "sợ hãi",
            "so": "sợ hãi",
            "fear": "sợ hãi",
            "ghê tởm": "ghê tởm",
            "ghê": "ghê tởm",
            "gh? t?m": "ghê tởm",  # Encoding sai
            "ghe tom": "ghê tởm",
            "ghe": "ghê tởm",
            "disgust": "ghê tởm"
        }
        
        # Thử map trực tiếp
        normalized = emotion_name_mapping.get(emotion_lower, emotion_lower)
        
        # Đảm bảo là một trong 6 cảm xúc chuẩn
        valid_emotions = ["vui", "buồn", "ngạc nhiên", "tức giận", "sợ hãi", "ghê tởm"]
        if normalized not in valid_emotions:
            # Thử tìm bằng cách so sánh từng từ
            for valid_emotion in valid_emotions:
                emotion_words = emotion_lower.split()
                valid_words = valid_emotion.split()
                if any(word in valid_emotion for word in emotion_words) or \
                   any(word in emotion_lower for word in valid_words):
                    normalized = valid_emotion
                    break
        
        # Nếu vẫn không tìm thấy, trả về tên gốc (có thể log warning)
        if normalized not in valid_emotions:
            print(f"⚠️ Warning: Could not normalize emotion '{emotion}' to standard name")
            return emotion_clean  # Trả về tên gốc nếu không map được
        
        return normalized
    
    def _build_request_description(self, emotion: str) -> str:
        """Sinh mô tả đơn giản cho yêu cầu biểu cảm."""
        mapping = {
            "vui": "Hãy cười thật tươi như khi con được khen nhé!",
            "ngạc nhiên": "Thể hiện nét mặt thật bất ngờ như vừa được tặng quà.",
            "buồn": "Thử làm gương mặt buồn bã khi nhớ một chuyện không vui.",
            "tức giận": "Hãy thể hiện nét mặt nghiêm và tức giận khi bị làm phiền.",
            "sợ hãi": "Thể hiện sự lo lắng, hoảng sợ như đang nghe tiếng sấm lớn.",
            "ghê tởm": "Thử nhăn mặt lại như ngửi phải mùi khó chịu.",
        }
        return mapping.get(emotion, f"Hãy thể hiện cảm xúc {emotion} nhé.")

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

    def _get_default_requests(self) -> List[dict]:
        """Trả về danh sách yêu cầu biểu cảm mặc định."""
        return [
            {
                "id": str(uuid4()),
                "title": "Nụ cười rực rỡ",
                "description": self._build_request_description("vui"),
                "target_emotion": "vui",
                "instruction": self._get_instruction("vui"),
                "hint": self._get_hint("vui"),
                "image_path": "",
                "explanation": "Gương mặt rạng rỡ giúp con lan tỏa sự tích cực cho mọi người.",
                "level": 1,
            },
            {
                "id": str(uuid4()),
                "title": "Ôi! Bất ngờ quá",
                "description": self._build_request_description("ngạc nhiên"),
                "target_emotion": "ngạc nhiên",
                "instruction": self._get_instruction("ngạc nhiên"),
                "hint": self._get_hint("ngạc nhiên"),
                "image_path": "",
                "explanation": "Khi bất ngờ, mắt và miệng của chúng ta mở to hơn bình thường.",
                "level": 1,
            },
            {
                "id": str(uuid4()),
                "title": "Mặt buồn hiu",
                "description": self._build_request_description("buồn"),
                "target_emotion": "buồn",
                "instruction": self._get_instruction("buồn"),
                "hint": self._get_hint("buồn"),
                "image_path": "",
                "explanation": "Biểu cảm buồn giúp con nhận biết và chia sẻ cảm xúc với người khác.",
                "level": 1,
            },
            {
                "id": str(uuid4()),
                "title": "Mình đang giận",
                "description": self._build_request_description("tức giận"),
                "target_emotion": "tức giận",
                "instruction": self._get_instruction("tức giận"),
                "hint": self._get_hint("tức giận"),
                "image_path": "",
                "explanation": "Tức giận là cảm xúc mạnh, hãy thử thể hiện thật nghiêm nhưng vẫn kiểm soát nhé.",
                "level": 1,
            },
            {
                "id": str(uuid4()),
                "title": "Hơi sợ một chút",
                "description": self._build_request_description("sợ hãi"),
                "target_emotion": "sợ hãi",
                "instruction": self._get_instruction("sợ hãi"),
                "hint": self._get_hint("sợ hãi"),
                "image_path": "",
                "explanation": "Khi lo sợ, cơ thể chúng ta thường căng lên và mắt mở to.",
                "level": 1,
            },
            {
                "id": str(uuid4()),
                "title": "Ôi, ghê quá!",
                "description": self._build_request_description("ghê tởm"),
                "target_emotion": "ghê tởm",
                "instruction": self._get_instruction("ghê tởm"),
                "hint": self._get_hint("ghê tởm"),
                "image_path": "",
                "explanation": "Nhăn mũi giúp con thể hiện sự khó chịu khi gặp điều bẩn.",
                "level": 1,
            },
        ]

    def start_session(self, user_id: str, game_type: str) -> dict:
        """Khởi tạo session cho game CV."""
        try:
            print(f"Starting session for user_id={user_id}, game_type={game_type}")
            
            # Tìm game CV - query trực tiếp từ database để tránh vấn đề với domain objects
            from app.models.games.game import Game as GameModel, GameTypeEnum
            cv_game_model = self.sessions_repo.db_session.query(GameModel).filter(
                GameModel.game_type == GameTypeEnum.GameCV
            ).first()
            
            if not cv_game_model:
                print("GameCV not found, creating new game...")
                # Tạo game CV nếu chưa có
                cv_game_model = GameModel(
                    game_id=uuid4(),
                    game_type=GameTypeEnum.GameCV,
                    name="Game CV - Nhận diện cảm xúc",
                    level=1,
                    difficulty_level=1,
                    max_errors=3,
                    level_threshold=5,
                    time_limit=300
                )
                self.sessions_repo.db_session.add(cv_game_model)
                self.sessions_repo.db_session.commit()
                self.sessions_repo.db_session.refresh(cv_game_model)
                print(f"Created new GameCV with id={cv_game_model.game_id}")
            
            game_id = cv_game_model.game_id
            print(f"Using GameCV with id={game_id}")
            
            # Kiểm tra user_id có tồn tại không
            from app.models.users.user import User as UserModel
            user_model = self.sessions_repo.db_session.query(UserModel).filter(
                UserModel.user_id == UUID(user_id)
            ).first()
            
            if not user_model:
                raise ValueError(f"User {user_id} not found in database")
            
            print(f"Found user: {user_model.user_id}")
            
            # Tạo session manually using model directly (more reliable)
            from app.models.sessions.session import Session as SessionModel, SessionStateEnum as ModelSessionStateEnum
            from datetime import datetime as dt
            
            # Sử dụng datetime.now() thay vì utcnow() để tránh timezone issues
            start_time = dt.now()
            
            session_model = SessionModel(
                session_id=uuid4(),
                user_id=UUID(user_id),
                game_id=game_id,
                start_time=start_time,
                state=ModelSessionStateEnum.playing,
                score=0,
                emotion_errors=json.dumps({"sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0}),
                max_errors=3,
                level_threshold=100,
                ratio=json.dumps([]),
                time_limit=300,
                question_ids=json.dumps([])
            )
            
            print(f"Creating session with: user_id={UUID(user_id)}, game_id={game_id}, start_time={start_time}")
            
            self.sessions_repo.db_session.add(session_model)
            try:
                print(f"💾 Committing session creation...")
                self.sessions_repo.db_session.commit()
                self.sessions_repo.db_session.refresh(session_model)
                
                # Verify session was saved
                saved_session = self.sessions_repo.db_session.query(SessionModel).filter(
                    SessionModel.session_id == session_model.session_id
                ).first()
                
                if saved_session:
                    print(f"✅ Verified: session saved to database with session_id={saved_session.session_id}")
                else:
                    print(f"⚠️ Warning: session not found in database after commit!")
                
            except Exception as commit_error:
                print(f"❌ Error committing session: {str(commit_error)}")
                import traceback
                print(traceback.format_exc())
                self.sessions_repo.db_session.rollback()
                raise
            
            print(f"✅ Session created successfully: session_id={session_model.session_id}")
            
            return {
                "session_id": str(session_model.session_id),
                "message": "Session started successfully"
            }
        except Exception as e:
            import traceback
            print(f"Error in start_session: {str(e)}")
            print(traceback.format_exc())
            self.sessions_repo.db_session.rollback()
            raise

    def save_result(self, session_id: UUID, scenario_id: UUID, 
                   target_emotion: str, detected_emotion: Optional[str],
                   success: bool, time_taken: int, confidence_score: float = 0.0,
                   check_hint: bool = False) -> dict:
        """Lưu kết quả của một bài."""
        try:
            # Get session
            session_model = self.sessions_repo.db_session.query(
                self.sessions_repo.model_class
            ).filter(
                self.sessions_repo.model_class.session_id == session_id
            ).first()
            
            if not session_model:
                return {"status": "error", "message": "Session not found"}
            
            # Try to get or create question from content_id (scenario_id)
            # If content doesn't exist (e.g., from default scenarios), skip session_questions
            question_model = None
            try:
                from app.models.games import Question as QuestionModel
                # Try to query with UUID
                try:
                    question_model = self.sessions_repo.db_session.query(QuestionModel).filter(
                        QuestionModel.content_id == scenario_id
                    ).first()
                except Exception as query_error:
                    print(f"Warning: Error querying question with UUID {scenario_id}: {str(query_error)}")
                    question_model = None
                
                # If question doesn't exist, try to create one from game_content
                if not question_model:
                    from app.models.games import GameContent as GameContentModel
                    try:
                        content_model = self.sessions_repo.db_session.query(GameContentModel).filter(
                            GameContentModel.content_id == scenario_id
                        ).first()
                    except Exception as query_error:
                        print(f"Warning: Error querying content with UUID {scenario_id}: {str(query_error)}")
                        content_model = None
                    
                    if content_model:
                        # Create question from content
                        question_model = QuestionModel(
                            question_id=uuid4(),
                            game_id=session_model.game_id,
                            level=content_model.level if hasattr(content_model, 'level') else 1,
                            content_id=scenario_id,
                            correct_answer=target_emotion
                        )
                        self.sessions_repo.db_session.add(question_model)
                        self.sessions_repo.db_session.flush()  # Flush to get question_id
                        print(f"Created new question for content {scenario_id}")
                    else:
                        # Content doesn't exist (e.g., default scenario), skip session_questions
                        print(f"ℹ️ Content {scenario_id} not found in database (likely default scenario), skipping session_questions")
            except Exception as e:
                print(f"Warning: Error processing question for scenario {scenario_id}: {str(e)}")
                import traceback
                print(traceback.format_exc())
                question_model = None
            
            # Get level from scenario to validate confidence threshold
            scenario_level = 1  # Default
            try:
                from app.models.games.game_content import GameContent as GameContentModel
                content_model = self.sessions_repo.db_session.query(GameContentModel).filter(
                    GameContentModel.content_id == scenario_id
                ).first()
                if content_model and hasattr(content_model, 'level'):
                    scenario_level = content_model.level or 1
                    print(f"   Scenario level: {scenario_level}")
            except Exception as e:
                print(f"   Warning: Could not get scenario level: {str(e)}")
            
            # Validate confidence score theo level threshold
            level_threshold = self.get_level_threshold(scenario_level)
            print(f"   Level {scenario_level} threshold: {level_threshold}%")
            
            # Override success nếu confidence không đạt ngưỡng
            # Lưu ý: FE đã check >= 1s, backend chỉ check confidence
            if success and confidence_score > 0 and confidence_score < level_threshold:
                print(f"   ⚠️ Confidence {confidence_score}% < threshold {level_threshold}% → Override success to False")
                success = False
            
            # Update session score: +1 mỗi màn pass (không phải +10)
            if success:
                session_model.score = (session_model.score or 0) + 1
                print(f"   ✅ Màn pass! Total score: {session_model.score} màn")
            
            # Update emotion errors (stored as JSON string in SQL Server)
            import json
            emotion_errors = {}
            if session_model.emotion_errors:
                if isinstance(session_model.emotion_errors, str):
                    try:
                        emotion_errors = json.loads(session_model.emotion_errors)
                    except (json.JSONDecodeError, ValueError):
                        emotion_errors = {}
                elif isinstance(session_model.emotion_errors, dict):
                    emotion_errors = session_model.emotion_errors.copy()
                else:
                    emotion_errors = {}
            
            # Ensure emotion_errors is a dict
            if not isinstance(emotion_errors, dict):
                emotion_errors = {}
            
            # Normalize tên cảm xúc ngay khi lưu để đảm bảo consistency
            emotion_normalized = self._normalize_emotion_name(target_emotion)
            print(f"📝 Saving result - Normalizing emotion: '{target_emotion}' -> '{emotion_normalized}'")
            print(f"   📊 Confidence score: {confidence_score}% (0-100), Success: {success}")
            
            # Initialize emotion entry if not exists
            if emotion_normalized not in emotion_errors:
                emotion_errors[emotion_normalized] = {"correct": 0, "incorrect": 0, "best_confidence": 0.0}
                print(f"   ✅ Initialized new emotion entry for '{emotion_normalized}'")
            elif not isinstance(emotion_errors[emotion_normalized], dict):
                emotion_errors[emotion_normalized] = {"correct": 0, "incorrect": 0, "best_confidence": 0.0}
                print(f"   🔄 Reset emotion entry for '{emotion_normalized}' (was not a dict)")
            
            # Update counts
            if success:
                emotion_errors[emotion_normalized]["correct"] = emotion_errors[emotion_normalized].get("correct", 0) + 1
            else:
                emotion_errors[emotion_normalized]["incorrect"] = emotion_errors[emotion_normalized].get("incorrect", 0) + 1
            
            # Lưu confidence score cao nhất (0-100) - CHỈ lưu khi success (confidence_score > 0)
            # Nếu confidence_score = 0, nghĩa là thất bại, không lưu điểm
            if success and confidence_score > 0:
                current_best = emotion_errors[emotion_normalized].get("best_confidence", 0.0)
                print(f"   📈 Current best confidence for '{emotion_normalized}': {current_best}%, New: {confidence_score}%")
                if confidence_score > current_best:
                    emotion_errors[emotion_normalized]["best_confidence"] = float(confidence_score)
                    print(f"   🎯 ✅ Updated best confidence for {emotion_normalized}: {confidence_score}% (was {current_best}%)")
                else:
                    print(f"   ⏸️  Best confidence not updated (new {confidence_score}% <= current {current_best}%)")
            else:
                print(f"   ❌ Not saving confidence score (success={success}, confidence_score={confidence_score}) - only save on success")
            
            # Save as JSON string for SQL Server
            session_model.emotion_errors = json.dumps(emotion_errors, ensure_ascii=False)
            print(f"Updated emotion_errors for {emotion_normalized}: {emotion_errors[emotion_normalized]}")
            
            # Save to session_questions - LUÔN tạo để track đầy đủ (dù không có question trong DB)
            try:
                from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
                
                # Tạo session_question model trực tiếp (không qua domain để tránh phụ thuộc question)
                session_question_model = SessionQuestionsModel(
                    id=uuid4(),
                    session_id=session_id,
                    question_id=question_model.question_id if question_model else None,  # NULL nếu không có question
                    user_answer=json.dumps({"detected_emotion": detected_emotion, "target_emotion": target_emotion}, ensure_ascii=False),
                    correct_answer=json.dumps({"target_emotion": target_emotion}, ensure_ascii=False),
                    is_correct=success,
                    response_time_ms=time_taken,
                    check_hint=check_hint,  # Lưu thông tin user có dùng hint hay không
                    cv_confidence=confidence_score / 100.0 if confidence_score > 0 else 0.0,  # Convert % to 0-1
                    timestamp=datetime.now()
                )
                
                self.sessions_repo.db_session.add(session_question_model)
                print(f"✅ Saved session_question for scenario {scenario_id} (question_id={session_question_model.question_id or 'NULL'})")
            except Exception as e:
                print(f"⚠️  Warning: Error saving session_question: {str(e)}")
                import traceback
                print(traceback.format_exc())
                # Continue even if session_questions save fails (không block việc lưu session)
            
            # Commit all changes
            try:
                self.sessions_repo.db_session.commit()
                print(f"✅ Result saved successfully for session {session_id}, scenario {scenario_id}")
                print(f"   Score updated to: {session_model.score}")
                print(f"   Emotion errors: {emotion_errors}")
            except Exception as commit_error:
                print(f"❌ Error committing save_result: {str(commit_error)}")
                import traceback
                print(traceback.format_exc())
                self.sessions_repo.db_session.rollback()
                raise
            
            return {
                "status": "success",
                "message": "Result saved successfully"
            }
        except Exception as e:
            import traceback
            print(f"Error in save_result: {str(e)}")
            print(traceback.format_exc())
            self.sessions_repo.db_session.rollback()
            return {"status": "error", "message": f"Error saving result: {str(e)}"}

    def end_session(self, session_id: UUID) -> dict:
        """Kết thúc session và lưu kết quả cuối cùng."""
        try:
            print(f"🔍 Ending session: {session_id}")
            # Get session
            session_model = self.sessions_repo.db_session.query(
                self.sessions_repo.model_class
            ).filter(
                self.sessions_repo.model_class.session_id == session_id
            ).first()

            if not session_model:
                print(f"❌ Session not found: {session_id}")
                return {"status": "error", "message": "Session not found"}
            
            print(f"✅ Found session: session_id={session_model.session_id}, user_id={session_model.user_id}, game_id={session_model.game_id}")

            # Update session state and end time
            from app.models.sessions.session import SessionStateEnum as ModelSessionStateEnum
            session_model.state = ModelSessionStateEnum.end
            end_time = datetime.now()
            session_model.end_time = end_time

            # Get level from first scenario in session (scenarios are already filtered by level)
            # If no scenarios, fallback to game level or 1
            level = 1
            try:
                from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
                from app.models.games.game_content import GameContent as GameContentModel
                
                # Get first session_question to find the scenario's level
                first_question = self.sessions_repo.db_session.query(SessionQuestionsModel).filter(
                    SessionQuestionsModel.session_id == session_id
                ).first()
                
                if first_question and first_question.content_id:
                    # Get the game_content to find its level
                    content = self.sessions_repo.db_session.query(GameContentModel).filter(
                        GameContentModel.content_id == first_question.content_id
                    ).first()
                    
                    if content and hasattr(content, 'level') and content.level:
                        level = content.level
                        print(f"📊 Level determined from first scenario: {level}")
                    else:
                        # Fallback to game level
                        game_model = self.sessions_repo.db_session.query(
                            self.games_repo.model_class
                        ).filter(
                            self.games_repo.model_class.game_id == session_model.game_id
                        ).first()
                        level = game_model.level if game_model and hasattr(game_model, 'level') else 1
                        print(f"📊 Level fallback to game level: {level}")
                else:
                    # No questions yet, use game level
                    game_model = self.sessions_repo.db_session.query(
                        self.games_repo.model_class
                    ).filter(
                        self.games_repo.model_class.game_id == session_model.game_id
                    ).first()
                    level = game_model.level if game_model and hasattr(game_model, 'level') else 1
                    print(f"📊 Level fallback (no questions): {level}")
            except Exception as e:
                print(f"⚠️ Error determining level, using default: {str(e)}")
                level = 1

            # Save to game_history (check if already exists to avoid duplicates)
            try:
                from app.models.analytics.game_history import GameHistory as GameHistoryModel
                existing_history = self.sessions_repo.db_session.query(GameHistoryModel).filter(
                    GameHistoryModel.session_id == session_id
                ).first()
                
                if not existing_history:
                    # Use user_id from session_model to ensure consistency
                    game_history_user_id = session_model.user_id
                    print(f"📝 Creating game_history for session {session_id}")
                    print(f"   Using user_id from session_model: {game_history_user_id}")
                    print(f"   Session user_id: {session_model.user_id}")
                    print(f"   Game_id: {session_model.game_id}")
                    print(f"   Score: {session_model.score or 0}")
                    print(f"   Level: {level}")
                    
                    game_history = GameHistory(
                        history_id=uuid4(),
                        user_id=game_history_user_id,  # Explicitly use session_model.user_id
                        session_id=session_id,
                        game_id=session_model.game_id,
                        score=session_model.score or 0,
                        level=level
                    )
                    game_history_model = self.game_history_repo.mapper_class.to_model(game_history)
                    print(f"   Created game_history_model with user_id: {game_history_model.user_id}")
                    self.sessions_repo.db_session.add(game_history_model)
                    print(f"✅ Added game_history: user_id={game_history_model.user_id}, score={session_model.score}, level={level}")
                else:
                    # Update existing history
                    print(f"📝 Updating existing game_history for session {session_id}")
                    print(f"   Current user_id in game_history: {existing_history.user_id}")
                    print(f"   Session user_id: {session_model.user_id}")
                    # Ensure user_id matches session (in case of inconsistency)
                    if existing_history.user_id != session_model.user_id:
                        print(f"⚠️ WARNING: user_id mismatch! game_history.user_id={existing_history.user_id} != session.user_id={session_model.user_id}")
                        print(f"   Updating game_history.user_id to match session.user_id")
                        existing_history.user_id = session_model.user_id
                    existing_history.score = session_model.score or 0
                    existing_history.level = level
                    print(f"✅ Updated existing game_history: user_id={existing_history.user_id}, score={session_model.score}, level={level}")
            except Exception as e:
                print(f"Warning: Error creating/updating game_history: {str(e)}")
                import traceback
                print(traceback.format_exc())

            # Save to session_history
            # Note: session_history requires child_id to exist in children table
            session_history_created = False
            try:
                from app.models.users.child import Child as ChildModel
                from app.models.analytics.session_history import SessionHistory as SessionHistoryModel
                from app.models.users.user import User as UserModel
                from app.domain.enum import RoleEnum, GenderEnum
                from datetime import date
                
                child_model = self.sessions_repo.db_session.query(ChildModel).filter(
                    ChildModel.user_id == session_model.user_id
                ).first()
                
                print(f"🔍 Checking child record for user_id={session_model.user_id}")
                if child_model:
                    print(f"✅ Child record found: user_id={child_model.user_id}")
                else:
                    print(f"⚠️ Child record not found, checking user role...")
                
                # If child doesn't exist but user has role="child", create child record automatically
                if not child_model:
                    user_model = self.sessions_repo.db_session.query(UserModel).filter(
                        UserModel.user_id == session_model.user_id
                    ).first()
                    
                    if user_model:
                        # Get role value - could be enum or string
                        role_value = user_model.role.value if hasattr(user_model.role, 'value') else str(user_model.role)
                        print(f"   User found: user_id={user_model.user_id}, role={user_model.role}, role_value={role_value}, role_type={type(user_model.role)}")
                        print(f"   RoleEnum.child={RoleEnum.child}, RoleEnum.child.value={RoleEnum.child.value}")
                        print(f"   Direct comparison: {user_model.role == RoleEnum.child}")
                        print(f"   String comparison: {role_value == 'child' or role_value == RoleEnum.child.value}")
                    else:
                        print(f"   ⚠️ User not found in database!")
                    
                    # Check role - handle both enum and string comparison
                    is_child = False
                    if user_model:
                        if hasattr(user_model.role, 'value'):
                            is_child = user_model.role.value == RoleEnum.child.value or user_model.role == RoleEnum.child
                        else:
                            is_child = str(user_model.role) == 'child' or str(user_model.role) == RoleEnum.child.value
                    
                    if user_model and is_child:
                        # Auto-create child record with default values
                        print(f"🔄 Child record not found for user {session_model.user_id}, creating automatically...")
                        
                        # Generate unique phone number from user_id
                        # Use full UUID without dashes, take last 11 digits to ensure uniqueness
                        full_uuid_no_dash = str(session_model.user_id).replace('-', '')
                        # Use last 11 digits (max 20 chars for phone_number column)
                        phone_suffix = full_uuid_no_dash[-11:]
                        default_phone = f"0{phone_suffix}"
                        
                        # Check if phone_number already exists, if so, use full UUID hash
                        max_attempts = 5
                        attempt = 0
                        while attempt < max_attempts:
                            existing_phone = self.sessions_repo.db_session.query(ChildModel).filter(
                                ChildModel.phone_number == default_phone
                            ).first()
                            
                            if not existing_phone:
                                break  # Phone is unique, use it
                            
                            # If phone exists, try different suffix
                            attempt += 1
                            if attempt < max_attempts:
                                # Try using more digits from UUID
                                offset = attempt * 2
                                phone_suffix = full_uuid_no_dash[-(11+offset):-offset] if (11+offset) <= len(full_uuid_no_dash) else full_uuid_no_dash
                                default_phone = f"0{phone_suffix[-11:]}"
                                print(f"   Phone conflict, trying alternative: {default_phone}")
                        
                        if attempt >= max_attempts:
                            # Last resort: use timestamp + UUID suffix
                            import time
                            timestamp_suffix = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
                            uuid_suffix = full_uuid_no_dash[-5:]  # Last 5 digits of UUID
                            default_phone = f"0{timestamp_suffix}{uuid_suffix}"
                            print(f"   Using timestamp-based phone: {default_phone}")
                        
                        try:
                            # Create child with default values
                            child_model = ChildModel(
                                user_id=session_model.user_id,
                                age=None,  # Optional
                                last_played=None,
                                report_preferences=None,
                                created_at=datetime.now(),
                                last_login=None,
                                gender=GenderEnum.other,  # Default gender
                                date_of_birth=date(2010, 1, 1),  # Default date of birth (can be updated later)
                                phone_number=default_phone
                            )
                            self.sessions_repo.db_session.add(child_model)
                            try:
                                self.sessions_repo.db_session.flush()  # Flush to ensure child record exists before creating session_history
                                print(f"✅ Created child record automatically for user {session_model.user_id}")
                                print(f"   Default phone: {default_phone} (can be updated later)")
                                print(f"   Child user_id (primary key): {child_model.user_id}")
                                
                                # Verify child was created
                                verify_child = self.sessions_repo.db_session.query(ChildModel).filter(
                                    ChildModel.user_id == session_model.user_id
                                ).first()
                                if verify_child:
                                    print(f"✅ Verified: Child record exists in database (user_id={verify_child.user_id})")
                                else:
                                    print(f"❌ ERROR: Child record was not found after flush!")
                            except Exception as flush_error:
                                print(f"❌ Error flushing child record: {str(flush_error)}")
                                import traceback
                                print(traceback.format_exc())
                                raise
                        except Exception as create_error:
                            print(f"❌ Error creating child record: {str(create_error)}")
                            import traceback
                            print(traceback.format_exc())
                            # Try to get child again in case it was created by another process
                            child_model = self.sessions_repo.db_session.query(ChildModel).filter(
                                ChildModel.user_id == session_model.user_id
                            ).first()
                            if child_model:
                                print(f"✅ Child record found after error (may have been created by another process)")
                            else:
                                print(f"⚠️ Could not create child record, session_history will be skipped")
                                child_model = None
                
                if child_model:
                    print(f"✅ Child model found/created: user_id={child_model.user_id}")
                    # Check if session_history already exists
                    existing_session_history = self.sessions_repo.db_session.query(SessionHistoryModel).filter(
                        SessionHistoryModel.session_id == session_id
                    ).first()
                    
                    if not existing_session_history:
                        # Child exists, can save session_history
                        print(f"📝 Creating new session_history for session {session_id}...")
                        try:
                            session_history = SessionHistory(
                                session_history_id=uuid4(),
                                child_id=session_model.user_id,
                                game_id=session_model.game_id,
                                session_id=session_id,
                                level=level,
                                start_time=session_model.start_time,
                                end_time=end_time,
                                score=session_model.score or 0
                            )
                            session_history_model = self.session_history_repo.mapper_class.to_model(session_history)
                            print(f"   session_history_id={session_history_model.session_history_id}")
                            print(f"   child_id={session_history_model.child_id}")
                            print(f"   game_id={session_history_model.game_id}")
                            print(f"   session_id={session_history_model.session_id}")
                            print(f"   level={session_history_model.level}")
                            print(f"   score={session_history_model.score}")
                            print(f"   start_time={session_history_model.start_time}")
                            print(f"   end_time={session_history_model.end_time}")
                            
                            # Double-check that child exists before adding session_history
                            verify_child_before_add = self.sessions_repo.db_session.query(ChildModel).filter(
                                ChildModel.user_id == session_model.user_id
                            ).first()
                            if not verify_child_before_add:
                                print(f"❌ ERROR: Child record not found before adding session_history! Cannot create session_history.")
                                raise Exception(f"Child record with user_id={session_model.user_id} does not exist")
                            
                            print(f"✅ Verified child exists before adding session_history (user_id={verify_child_before_add.user_id})")
                            
                            self.sessions_repo.db_session.add(session_history_model)
                            print(f"✅ Added session_history to session (pending commit) for child {session_model.user_id}")
                            
                            # Try to flush session_history to catch any FK constraint errors early
                            try:
                                self.sessions_repo.db_session.flush()
                                print(f"✅ Flushed session_history successfully (no FK constraint errors)")
                                session_history_created = True
                            except Exception as flush_error:
                                print(f"❌ ERROR flushing session_history: {str(flush_error)}")
                                import traceback
                                print(traceback.format_exc())
                                # Check if child still exists
                                verify_child_after_error = self.sessions_repo.db_session.query(ChildModel).filter(
                                    ChildModel.user_id == session_model.user_id
                                ).first()
                                if verify_child_after_error:
                                    print(f"   Child still exists: user_id={verify_child_after_error.user_id}")
                                else:
                                    print(f"   ❌ Child does NOT exist! This is the problem.")
                                raise
                        except Exception as create_error:
                            print(f"❌ Error creating session_history object: {str(create_error)}")
                            import traceback
                            print(traceback.format_exc())
                            # Don't raise here - let it be caught by outer exception handler
                            # But mark that session_history was not created
                            session_history_created = False
                    else:
                        # Update existing session_history
                        print(f"📝 Updating existing session_history for session {session_id}...")
                        existing_session_history.score = session_model.score or 0
                        existing_session_history.end_time = end_time
                        existing_session_history.level = level
                        print(f"✅ Updated existing session_history for child {session_model.user_id}")
                else:
                    # User is not a child, skip session_history
                    print(f"ℹ️ User {session_model.user_id} is not a child or child record creation failed, skipping session_history")
            except Exception as e:
                print(f"❌ CRITICAL ERROR creating/updating session_history: {str(e)}")
                import traceback
                print(traceback.format_exc())
                print(f"⚠️ Session_history creation failed, but continuing with game_history save...")
                session_history_created = False
                # Continue even if session_history fails - game_history is more important
            if isinstance(session_model.emotion_errors, dict):
                session_model.emotion_errors = json.dumps(session_model.emotion_errors, ensure_ascii=False)
            
            # Save to child_progress - logic phụ thuộc vào game type
            try:
                from app.models.users.child import Child as ChildModel
                from app.models.analytics.child_progress import ChildProgress as ChildProgressModel
                from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
                from app.models.sessions.session import Session as SessionModel
                from app.models.games.game import Game as GameModel
                
                child_model = self.sessions_repo.db_session.query(ChildModel).filter(
                    ChildModel.user_id == session_model.user_id
                ).first()
                
                if child_model:
                    # Lấy game để kiểm tra game_type
                    game_model = self.sessions_repo.db_session.query(GameModel).filter(
                        GameModel.game_id == session_model.game_id
                    ).first()
                    
                    if not game_model:
                        print(f"⚠️ Game not found for session {session_id}")
                        raise Exception("Game not found")
                    
                    print(f"📊 Calculating child_progress for child {child_model.user_id}...")
                    print(f"   Game: {game_model.name}")
                    
                    # Phân biệt logic dựa vào tên game
                    # Game có chứa "yêu cầu" hoặc "request" trong tên -> emotion-based scoring
                    game_name_lower = game_model.name.lower() if game_model.name else ""
                    is_request_mode = "yêu cầu" in game_name_lower or "request" in game_name_lower or "yeu cau" in game_name_lower
                    
                    if is_request_mode:
                        # Game "Biểu cảm theo yêu cầu" - tính điểm theo best emotion average
                        print(f"   → Using EMOTION-BASED scoring (detected 'request' mode)")
                        self._update_child_progress_emotion_based(
                            child_model, session_model, session_id, end_time, level
                        )
                    else:
                        # Game "Biểu cảm theo tình huống" - tính điểm theo màn/session
                        print(f"   → Using SESSION-BASED scoring (scenario mode)")
                        self._update_child_progress_session_based(
                            child_model, session_model, session_id, end_time, level
                        )
                else:
                    print(f"ℹ️ User {session_model.user_id} is not a child, skipping child_progress")
            except Exception as e:
                print(f"Warning: Error creating/updating child_progress: {str(e)}")
                import traceback
                print(traceback.format_exc())
                # Continue even if child_progress fails
            
            # Flush all changes before commit to catch any errors early
            try:
                print(f"🔄 Flushing changes to database...")
                self.sessions_repo.db_session.flush()
                print(f"✅ Flush successful")
            except Exception as flush_error:
                print(f"❌ Error flushing changes: {str(flush_error)}")
                import traceback
                print(traceback.format_exc())
                self.sessions_repo.db_session.rollback()
                raise
            
            # Commit all changes
            try:
                print(f"💾 Committing transaction for session {session_id}...")
                self.sessions_repo.db_session.commit()
                print(f"✅ Commit successful")
                
                # Refresh to get latest data
                self.sessions_repo.db_session.refresh(session_model)
                
                # Verify data was saved
                from app.models.analytics.game_history import GameHistory as GameHistoryModel
                saved_history = self.sessions_repo.db_session.query(GameHistoryModel).filter(
                    GameHistoryModel.session_id == session_id
                ).first()
                
                if saved_history:
                    print(f"✅ Verified: game_history saved with score={saved_history.score}, level={saved_history.level}")
                else:
                    print(f"⚠️ Warning: game_history not found after commit!")
                
                # Verify session_history was saved
                from app.models.analytics.session_history import SessionHistory as SessionHistoryModel
                saved_session_history = self.sessions_repo.db_session.query(SessionHistoryModel).filter(
                    SessionHistoryModel.session_id == session_id
                ).first()
                
                if saved_session_history:
                    print(f"✅ Verified: session_history saved with score={saved_session_history.score}, level={saved_session_history.level}, child_id={saved_session_history.child_id}")
                else:
                    if session_history_created:
                        print(f"❌ CRITICAL: session_history was created and flushed but NOT found after commit!")
                        print(f"   This indicates a serious problem - session_history was lost during commit.")
                    else:
                        print(f"⚠️ Warning: session_history not found after commit! This might be normal if:")
                        print(f"   - User is not a child")
                        print(f"   - Child record creation failed")
                        print(f"   - Session_history creation encountered an error")
                
                print(f"✅ Session {session_id} ended and saved successfully")
                print(f"   Score: {session_model.score}")
                print(f"   Game History and Session History saved")
            except Exception as commit_error:
                print(f"❌ Error committing end_session: {str(commit_error)}")
                import traceback
                print(traceback.format_exc())
                self.sessions_repo.db_session.rollback()
                raise

            # Prepare emotion_errors for response (convert JSON string to dict)
            emotion_errors = session_model.emotion_errors or "{}"
            if isinstance(emotion_errors, str):
                try:
                    emotion_errors = json.loads(emotion_errors)
                except (json.JSONDecodeError, ValueError):
                    emotion_errors = {}
            elif not isinstance(emotion_errors, dict):
                emotion_errors = {}

            return {
                "status": "success",
                "message": "Session ended successfully",
                "session_id": str(session_model.session_id),
                "score": session_model.score or 0,
                "emotion_errors": emotion_errors
            }
        except Exception as e:
            import traceback
            print(f"Error in end_session: {str(e)}")
            print(traceback.format_exc())
            self.sessions_repo.db_session.rollback()
            return {"status": "error", "message": f"Error ending session: {str(e)}"}
    
    def _update_child_progress_emotion_based(self, child_model, session_model, session_id: UUID, end_time, level: int):
        """
        Cập nhật child_progress dựa trên điểm trung bình của các cảm xúc (cho game 'Yêu cầu').
        Mỗi cảm xúc có best_confidence, tính accuracy = average của 6 cảm xúc.
        """
        try:
            from app.models.analytics.child_progress import ChildProgress as ChildProgressModel
            import json
            
            print(f"   📊 Updating child_progress (EMOTION-BASED) for child {child_model.user_id}...")
            
            # Parse emotion_errors to get best_confidence for each emotion
            emotion_errors = session_model.emotion_errors
            if isinstance(emotion_errors, str):
                try:
                    emotion_errors = json.loads(emotion_errors)
                except:
                    emotion_errors = {}
            
            if not isinstance(emotion_errors, dict):
                emotion_errors = {}
            
            # Calculate average accuracy from emotion scores (best_confidence of each emotion)
            valid_emotions = ["vui", "buồn", "ngạc nhiên", "tức giận", "sợ hãi", "ghê tởm"]
            emotion_scores = []
            
            for emotion in valid_emotions:
                if emotion in emotion_errors and isinstance(emotion_errors[emotion], dict):
                    best_conf = emotion_errors[emotion].get("best_confidence", 0.0)
                    emotion_scores.append(float(best_conf))
                    print(f"      {emotion}: {best_conf}%")
                else:
                    emotion_scores.append(0.0)
                    print(f"      {emotion}: 0% (not played)")
            
            # Accuracy = average of all emotion scores (0-100)
            accuracy = sum(emotion_scores) / len(emotion_scores) if emotion_scores else 0.0
            print(f"   📊 Calculated accuracy (emotion average): {accuracy:.2f}%")
            
            # Get or create child_progress for this game+level
            progress = self.sessions_repo.db_session.query(ChildProgressModel).filter(
                ChildProgressModel.child_id == child_model.user_id,
                ChildProgressModel.game_id == session_model.game_id,
                ChildProgressModel.level == level
            ).first()
            
            # Calculate avg_response_time from session_questions
            from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
            session_questions = self.sessions_repo.db_session.query(SessionQuestionsModel).filter(
                SessionQuestionsModel.session_id == session_id
            ).all()
            
            total_time = 0
            count = 0
            for sq in session_questions:
                if sq.response_time_ms and sq.response_time_ms > 0:
                    total_time += sq.response_time_ms
                    count += 1
            
            avg_response_time = (total_time / count / 1000.0) if count > 0 else 0.0  # Convert to seconds
            
            if progress:
                # Update existing progress: chỉ cập nhật nếu accuracy mới cao hơn
                print(f"   📝 Found existing progress (score={progress.score}, accuracy={progress.accuracy}%)")
                if accuracy > progress.accuracy:
                    progress.accuracy = accuracy
                    progress.score = session_model.score or 0
                    progress.avg_response_time = avg_response_time
                    progress.last_played = end_time
                    print(f"   ✅ Updated progress: accuracy={accuracy:.2f}%, score={session_model.score}")
                else:
                    # Chỉ update last_played
                    progress.last_played = end_time
                    print(f"   ⏸️  Accuracy not improved ({accuracy:.2f}% <= {progress.accuracy}%), only updated last_played")
            else:
                # Create new progress
                print(f"   📝 Creating new progress entry...")
                progress = ChildProgressModel(
                    progress_id=uuid4(),
                    child_id=child_model.user_id,
                    game_id=session_model.game_id,
                    level=level,
                    accuracy=accuracy,
                    avg_response_time=avg_response_time,
                    score=session_model.score or 0,
                    last_played=end_time,
                    ratio='[]',  # JSON string (SQL Server không hỗ trợ ARRAY)
                    review_emotions='[]'  # JSON string
                )
                self.sessions_repo.db_session.add(progress)
                print(f"   ✅ Created new progress: accuracy={accuracy:.2f}%, score={session_model.score}, level={level}")
        except Exception as e:
            print(f"   ❌ Error in _update_child_progress_emotion_based: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def _update_child_progress_session_based(self, child_model, session_model, session_id: UUID, end_time, level: int):
        """
        Cập nhật child_progress dựa trên số màn pass trong session (cho game 'Tình huống').
        Mỗi session = 10 màn (scenarios), score = số màn pass.
        Accuracy = (số màn pass / tổng số màn đã chơi) * 100%
        """
        try:
            from app.models.analytics.child_progress import ChildProgress as ChildProgressModel
            from app.models.sessions.session_questions import SessionQuestions as SessionQuestionsModel
            import json
            
            print(f"   📊 Updating child_progress (SESSION-BASED) for child {child_model.user_id}...")
            
            # Get or create child_progress for this game+level
            progress = self.sessions_repo.db_session.query(ChildProgressModel).filter(
                ChildProgressModel.child_id == child_model.user_id,
                ChildProgressModel.game_id == session_model.game_id,
                ChildProgressModel.level == level
            ).first()
            
            # Calculate accuracy from session_questions
            session_questions = self.sessions_repo.db_session.query(SessionQuestionsModel).filter(
                SessionQuestionsModel.session_id == session_id
            ).all()
            
            correct_count = sum(1 for sq in session_questions if sq.is_correct)
            total_count = len(session_questions)
            
            # Accuracy = % câu đúng trong session này
            session_accuracy = (correct_count / total_count * 100.0) if total_count > 0 else 0.0
            print(f"   📊 Session accuracy: {correct_count}/{total_count} = {session_accuracy:.2f}%")
            
            # Calculate avg_response_time
            total_time = 0
            count = 0
            for sq in session_questions:
                if sq.response_time_ms and sq.response_time_ms > 0:
                    total_time += sq.response_time_ms
                    count += 1
            
            avg_response_time = (total_time / count / 1000.0) if count > 0 else 0.0  # Convert to seconds
            
            # Score trong game tình huống = tổng số màn pass tích lũy (cộng dồn qua các session)
            # Mỗi session thêm số màn pass vào score
            current_session_score = session_model.score or 0  # Số màn pass trong session này
            
            if progress:
                # Update existing progress
                print(f"   📝 Found existing progress (score={progress.score}, accuracy={progress.accuracy}%)")
                
                # Score = tích lũy số màn pass qua các session
                progress.score = (progress.score or 0) + current_session_score
                
                # Accuracy = trung bình trượt (weighted average) hoặc max
                # Chọn cách đơn giản: lấy accuracy cao nhất giữa session này và session trước
                if session_accuracy > progress.accuracy:
                    progress.accuracy = session_accuracy
                
                progress.avg_response_time = avg_response_time
                progress.last_played = end_time
                
                print(f"   ✅ Updated progress: score={progress.score} (+{current_session_score}), accuracy={progress.accuracy:.2f}%")
            else:
                # Create new progress
                print(f"   📝 Creating new progress entry...")
                progress = ChildProgressModel(
                    progress_id=uuid4(),
                    child_id=child_model.user_id,
                    game_id=session_model.game_id,
                    level=level,
                    accuracy=session_accuracy,
                    avg_response_time=avg_response_time,
                    score=current_session_score,  # Số màn pass trong session đầu tiên
                    last_played=end_time,
                    ratio='[]',  # JSON string (SQL Server không hỗ trợ ARRAY)
                    review_emotions='[]'  # JSON string
                )
                self.sessions_repo.db_session.add(progress)
                print(f"   ✅ Created new progress: score={current_session_score} màn, accuracy={session_accuracy:.2f}%, level={level}")
        except Exception as e:
            print(f"   ❌ Error in _update_child_progress_session_based: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

