from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.base import Base 
from dotenv import load_dotenv
import os

load_dotenv(r"D:\TTNM\TTNM-Game\be\app\.env")

DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")
print("DATABASE_URL =", DATABASE_URL)  # kiểm tra giá trị

engine = create_engine(DATABASE_URL)

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