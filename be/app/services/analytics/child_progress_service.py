from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.repository.child_progress_repo import ChildProgressRepository
from app.domain.analytics.child_progress import ChildProgress
from app.domain.sessions.session import Session, SessionStateEnum
from app.mapper.child_progress_mapper import ChildProgressMapper


class ChildProgressService:
    def __init__(self, progress_repo: ChildProgressRepository):
        self.progress_repo = progress_repo
        self.mapper = ChildProgressMapper

    # Lấy tiến trình hiện tại hoặc tạo mới nếu chưa có.
    def get_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        progress  = self.progress_repo.get_progress(child_id, game_id)
        return progress

    def get_current_level(self, child_id: UUID, game_id: UUID) -> int:
        progress = self.get_progress(child_id, game_id)
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
            emotion_errors={},
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
    
    # update và trả về progress đã cập nhật
    def update_progress_after_session(self, child_id: UUID, game_id: UUID, session: Session) -> ChildProgress:
        """
        Cập nhật tiến trình sau khi chơi xong một session.
        Tính lại accuracy, score, ratio, review_emotions, level...
        """
        print("a")
        progress = self.progress_repo.get_progress(child_id, game_id)
        print("progress: ", progress.progress_id, ". ",progress.child_id, ". ",progress.game_id, ". ",progress.level, ". score: ",progress.score, ". ",progress.ratio)
        print("2 :", progress.accuracy, ". ",progress.review_emotions)
        print("aa ", progress.child_id)
        progress.accuracy = progress.calculate_accuracy([session]) # mất acc
        print("progress: ", progress.progress_id, ". ",progress.child_id, ". ",progress.game_id, ". ",progress.level, ". score: ",progress.score,". ",progress.ratio)
        print("2 :", progress.accuracy, ". ",progress.review_emotions)
        progress.score += sum(getattr(q, "score", 0) for q in getattr(session, "session_questions", []))
        print("a1")
        print("progress: ", progress.progress_id, ". ",progress.child_id, ". ",progress.game_id, ". ",progress.level, ". score: ",progress.score,". ",progress.ratio)
        print("2 :", progress.accuracy, ". ",progress.review_emotions)
        # Cập nhật phân bố cảm xúc và review_emotions
        progress.update_emotion_distribution()
        print("a2")
        print("progress: ", progress.progress_id, ". ",progress.child_id, ". ",progress.game_id, ". ",progress.level, ". score: ",progress.score,". ",progress.ratio)
        print("2 :", progress.accuracy, ". ",progress.review_emotions)
        # Kiểm tra lên level nếu đạt threshold
        level_threshold = getattr(session, "level_threshold", 70)
        print(";level thread:", level_threshold)
        if progress.check_level_advance(progress.score, level_threshold):
            progress.level += 1

        # Lưu tiến trình vào DB
        print("a4")
        print("progress: ", progress.progress_id, ". ",progress.child_id, ". ",progress.game_id, ". ",progress.level, ". score: ",progress.score,". ",progress.ratio)
        print("2 :", progress.accuracy, ". ",progress.review_emotions)
        self.progress_repo.update(progress)
        print("a5")
        return progress
