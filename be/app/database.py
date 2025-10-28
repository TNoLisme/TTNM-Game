from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.base import Base  # Import từ base.py
from dotenv import load_dotenv
import os

# Load biến môi trường
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")

# Tạo engine kết nối CSDL
engine = create_engine(DATABASE_URL)

# Tạo SessionLocal để thao tác DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm dependency để lấy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Kết nối SQL Server thành công!")
    except Exception as e:
        print("❌ Lỗi kết nối:", e)