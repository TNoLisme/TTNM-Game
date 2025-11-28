from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.repository.child_progress_repo import ChildProgressRepository
from app.domain.analytics.child_progress import ChildProgress
from app.domain.sessions.session import Session, SessionStateEnum


class ChildProgressService:
    def __init__(self, db: Session):
        self.progress_repo = ChildProgressRepository(db)

    # Lấy tiến trình hiện tại hoặc tạo mới nếu chưa có
    def get_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        progress = self.progress_repo.get_progress(child_id, game_id)
        print("=== get_progress ===")
        print(f"Child: {child_id}, Game: {game_id}, Level: {progress.level}, Score: {progress.score}, Ratio: {progress.ratio}")
        return progress

    # Lấy level hiện tại của user
    def get_current_level(self, child_id: UUID, game_id: UUID) -> int:
        progress = self.get_progress(child_id, game_id)
        return progress.level

    # Lấy ratio hiện tại của user
    def get_ratio(self, child_id: UUID, game_id: UUID) -> List[float]:
        progress = self.get_progress(child_id, game_id)
        default_ratio = [0.1667]*5 + [0.1665]
        if not progress or not progress.ratio or all(r == 0 for r in progress.ratio):
            return default_ratio
        return progress.ratio

    # Tạo session mới cho user
    def start_session(self, child_id: UUID, game_id: UUID, level: int) -> Session:
        session = Session(
            session_id=uuid4(),
            user_id=child_id,
            game_id=game_id,
            start_time=datetime.utcnow(),
            state=SessionStateEnum.playing,
            score=0,
            emotion_errors={},
            max_errors=3,
            level_threshold=100,  # có thể lấy từ game config
            ratio=self.get_ratio(child_id, game_id),
            time_limit=60,
            questions=[],
            level=level
        )
        print("=== start_session ===")
        print(f"SessionID: {session.session_id}, User: {child_id}, Game: {game_id}, Level: {level}")
        return session

    # Cập nhật tiến trình sau khi kết thúc session
    def update_progress_after_session(self, child_id: UUID, game_id: UUID, session: Session) -> ChildProgress:
        progress = self.progress_repo.get_progress(child_id, game_id)
        print("=== Before update_progress_after_session ===")
        print(f"ProgressID: {progress.progress_id}, Level: {progress.level}, Score: {progress.score}, Ratio: {progress.ratio}")

        # Tính accuracy dựa trên session
        progress.accuracy = progress.calculate_accuracy([session])
        # Cộng score từ các session_questions
        progress.score += sum(getattr(q, "score", 0) for q in getattr(session, "session_questions", []))
        # Cập nhật review_emotions và ratio
        progress.update_emotion_distribution()

        # Kiểm tra lên level nếu đạt threshold
        level_threshold = getattr(session, "level_threshold", 70)
        if progress.check_level_advance(progress.score, level_threshold):
            progress.level += 1
            print(f"Level advanced! New Level: {progress.level}")

        # Lưu tiến trình
        updated_progress = self.progress_repo.update(progress)
        print("=== After update_progress_after_session ===")
        print(f"ProgressID: {updated_progress.progress_id}, Level: {updated_progress.level}, Score: {updated_progress.score}, Ratio: {updated_progress.ratio}")
        return updated_progress
