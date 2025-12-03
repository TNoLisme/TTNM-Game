from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.repository.child_progress_repo import ChildProgressRepository
from app.domain.analytics.child_progress import ChildProgress
from app.domain.sessions.session import Session, SessionStateEnum
from app.mapper.child_progress_mapper import ChildProgressMapper


class ChildProgressService:
    def __init__(self, db: Session):
        self.progress_repo = ChildProgressRepository(db)
        self.mapper = ChildProgressMapper

    # Lấy tiến trình hiện tại hoặc tạo mới nếu chưa có.
    def get_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        progress  = self.progress_repo.get_progress(child_id, game_id)
        return progress

    def get_current_level(self, child_id: UUID, game_id: UUID) -> int:
        progress = self.progress_repo.get_progress(child_id, game_id)
        return progress.level

    def start_session(self, child_id: UUID, game_id: UUID, level: int) -> Session:
        from uuid import uuid4
        from datetime import datetime

        session = Session(
            session_id=uuid4(),
            user_id=child_id,
            game_id=game_id,
            start_time=datetime.utcnow(),
            state=SessionStateEnum.playing,
            score=0,
            emotion_errors={"sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0},
            max_errors=3,
            level_threshold=100,
            ratio=[0.0]*6,
            time_limit=60,
            questions=[],
            level=1
        )
        return session

    # Lấy mảng ratio của user theo từng game 
    def get_ratio(self, user_id: UUID, game_id: UUID) -> List[float]:

        progress = self.progress_repo.get_progress(user_id, game_id)

        default_ratio = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665]  # 6 emotions

        if not progress or not progress.ratio or all(r == 0 for r in progress.ratio):
            return default_ratio
        return progress.ratio
    
    def update_progress_after_session(self, child_id: UUID, game_id: UUID, session: Session, old_emotion_error: dict, review_emotions: List[str] = None ) -> ChildProgress:
        """
        Cập nhật tiến trình sau khi chơi xong một session.
        Tính lại accuracy, score, ratio, review_emotions, level.
        """
        progress = self.progress_repo.get_progress(child_id, game_id)
        
        # 1. TÍNH TOÁN ACCURACY MỚI
        total_questions = len(session.questions)
        if total_questions > 0:
            total_score_possible = total_questions * 10 
            accuracy = (session.score / total_score_possible) * 100 
        else:
            accuracy = 0.0
            print("Không có câu hỏi nào được lưu trong session_questions để tính Accuracy.")

        progress.accuracy = accuracy
        progress.score += session.score # Cộng dồn điểm mới vào tổng điểm
        
        # 2. Cập nhật review_emotions
        if review_emotions:
            if progress.review_emotions is None:
                progress.review_emotions = []
            
            # Sử dụng set để thêm các cảm xúc mới mà không trùng lặp
            unique_review_emotions = list(set(progress.review_emotions) | set(review_emotions))
            progress.review_emotions = unique_review_emotions

        # 3. Cập nhật phân bố cảm xúc
        # LƯU Ý: Hàm update_emotion_distribution_from_session trong ChildProgress domain phải được sửa
        progress.update_emotion_distribution_from_session(session, old_emotion_error)
        
        # 4. Kiểm tra lên level
        level_threshold = 30 # Test value
        
        # Giả định ChildProgress có hàm check_level_advance(self, score, threshold) trả về bool
        progress = progress.check_level_advance(progress, level_threshold, session)


        # Lưu tiến trình vào DB
        self.progress_repo.update(progress)
        return progress