# test_child_progress.py
from uuid import uuid4
from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.models.analytics.child_progress import ChildProgress

# ---- Cấu hình DB ----
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# UUID phải ở dạng STRING khi dùng với SQL Server qua pyodbc
TEST_USER_ID = "7B732DC2-21F1-4369-AF77-098668261CBF"
TEST_GAME_ID = "51547AAF-A4E2-4EEE-9408-D9E73423103A"

def test_save_ratio():
    db = SessionLocal()
    try:
        ratio_list = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665]
        review_emotions_list = [str(uuid4()), str(uuid4())]

        progress = ChildProgress(
            progress_id=str(uuid4()),        # luôn là str
            child_id=TEST_USER_ID,
            game_id=TEST_GAME_ID,
            level=1,
            score=0,
            accuracy=0.0,
            avg_response_time=0.0,
            last_played=datetime.utcnow(),
            ratio=json.dumps(ratio_list),
            review_emotions=json.dumps(review_emotions_list)
        )

        db.add(progress)
        db.commit()
        print("✅ Đã lưu thành công!")

        saved = db.query(ChildProgress)\
                  .filter_by(progress_id=progress.progress_id)\
                  .first()

        if saved:
            print("🔹 ratio:", json.loads(saved.ratio))
            print("🔹 review_emotions:", json.loads(saved.review_emotions))
        else:
            print("❌ Không tìm thấy record!")

    except Exception as e:
        print("❌ Lỗi khi lưu:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_save_ratio()
