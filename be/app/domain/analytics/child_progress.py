from uuid import UUID
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.domain.sessions.session import Session

class ChildProgress:
    def __init__(self,progress_id: UUID,child_id: UUID,game_id: UUID,level: int,accuracy: float,avg_response_time: float,score: int,
        last_played: datetime,ratio: List[float],review_emotions: List[UUID]):
        self.progress_id = progress_id
        self.child_id = child_id
        self.game_id = game_id
        self.level = level
        self.accuracy = accuracy
        self.avg_response_time = avg_response_time
        self.score = score
        self.last_played = last_played
        self.ratio = ratio
        self.review_emotions = review_emotions        

    def calculate_accuracy(self, sessions: List['Session']) -> float:
        """
        Tính tỷ lệ trả lời đúng (%) dựa trên danh sách các session.
        Accuracy = (Tổng số câu trả lời đúng) / (Tổng số câu trả lời) * 100
        """
        total_questions = 0
        total_correct = 0

        for session in sessions:
            questions = getattr(session, "session_questions", [])
            total_questions += len(questions)
            total_correct += sum(1 for q in questions if getattr(q, "is_correct", False))

        if total_questions == 0:
            print("Không có câu hỏi nào, accuracy = 0%")
            return 0.0

        accuracy = (total_correct / total_questions) * 100
        print(f"Tổng câu hỏi: {total_questions}, Đúng: {total_correct}, Accuracy mới: {accuracy:.2f}%")
        return accuracy

    def update_emotion_distribution_from_session(self, session: 'Session', old_emotion_error: dict) -> List[float]:
        """
        Cập nhật ratio dựa trên emotion_errors từ session vừa chơi.
        Tăng tỷ trọng của các cảm xúc bị sai và giảm tỷ trọng của các cảm xúc khác.
        """
        print(f"[update_emotion_distribution_from_session] Lỗi trong Session: {session.emotion_errors}")

        EMOTION_TO_INDEX = {
            "vui vẻ": 0,
            "buồn bã": 1,
            "tức giận": 2,
            "sợ hãi": 3,
            "ngạc nhiên": 4,
            "ghê tởm": 5
        }
        NUM_EMOTIONS = len(EMOTION_TO_INDEX)
        
        # Đảm bảo ratio tồn tại và có kích thước đúng
        if not self.ratio or len(self.ratio) != NUM_EMOTIONS:
            default_ratio = [1.0 / NUM_EMOTIONS] * NUM_EMOTIONS
            # Làm tròn số cuối để tổng là 1.0
            default_ratio[-1] = 1.0 - sum(default_ratio[:-1])
            self.ratio = default_ratio

        if not session.emotion_errors:
            return self.ratio

        # Tính tổng số lỗi mới
        total_session_errors = sum(session.emotion_errors.values())
        if total_session_errors == 0:
            return self.ratio

        # Định nghĩa tốc độ học (Learning Rate)
        LEARNING_RATE_TOTAL = 0.15 
        
        # Chuẩn hóa key và CHỈ LẤY NHỮNG CẢM XÚC CÓ LỖI (> 0)
        normalized_errors = {k.strip().lower(): v for k, v in session.emotion_errors.items() if v > 0}
        
        # Tính toán tỷ trọng (Weight) cần điều chỉnh
        adjustment_weights = {}
        for emotion, error_count in normalized_errors.items():
            if emotion in EMOTION_TO_INDEX:
                adjustment_weights[emotion] = error_count / total_session_errors
        
        # Phân bổ lại Ratio
        new_ratio = list(self.ratio)
        total_non_error_ratio = 0.0
        emotions_with_errors = normalized_errors.keys()

        # Tính tổng tỷ trọng của các cảm xúc KHÔNG bị lỗi
        for emotion, idx in EMOTION_TO_INDEX.items():
            if emotion not in emotions_with_errors:
                total_non_error_ratio += self.ratio[idx]
        
        # Giới hạn số lượng tỷ trọng có thể chuyển đi
        transfer_amount = min(LEARNING_RATE_TOTAL, total_non_error_ratio)

        # GIẢM tỷ trọng của các cảm xúc KHÔNG bị lỗi
        for emotion, idx in EMOTION_TO_INDEX.items():
            if emotion not in emotions_with_errors:
                # Giảm tỷ lệ dựa trên tỷ trọng cũ của nó
                if total_non_error_ratio > 0:
                    reduction = (self.ratio[idx] / total_non_error_ratio) * transfer_amount
                else:
                    reduction = 0
                new_ratio[idx] -= reduction

        # TĂNG tỷ trọng của các cảm xúc BỊ LỖI
        for emotion, idx in EMOTION_TO_INDEX.items():
            if emotion in emotions_with_errors:
                # Tăng tỷ lệ dựa trên weight (tỷ lệ lỗi)
                increase = adjustment_weights[emotion] * transfer_amount
                new_ratio[idx] += increase
                print(f"  → Tăng ratio của '{emotion}' (index {idx}): +{increase:.4f}")

        # Đảm bảo tổng là 1.0 và làm tròn
        final_total = sum(new_ratio)
        if final_total > 0:
            self.ratio = [round(r / final_total, 4) for r in new_ratio]
        else:
            self.ratio = new_ratio
        
        # Cập nhật lại vào session để trả về FE nếu cần
        session.ratio = self.ratio
        
        return self.ratio

    def generate_report(self, report_type: str) -> dict:
        """Tạo báo cáo tiến trình."""
        return {"type": report_type, "accuracy": self.accuracy}

    def check_level_advance(self, progress, level_threshold: int, session: 'Session'):
        """Kiểm tra xem có đủ điểm để lên level không."""
        if session.level == progress.level and progress.score >= level_threshold:
            progress.accuracy = 0
            progress.score = 0
            progress.level += 1
            progress.ratio = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665]
            session.ratio = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665]
            session.emotion_errors = {"sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0}
            progress.review_emotions = []
            
        return progress
