from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from app.base import Base  # (Giữ nguyên import của bạn)
from dotenv import load_dotenv
import os

# Load biến môi trường
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")

# --- PHẦN SỬA ĐỔI QUAN TRỌNG ---
# Kiểm tra và thêm charset=utf8 vào chuỗi kết nối nếu chưa có
if DATABASE_URL and "charset=utf8" not in DATABASE_URL:
    # Vì URL của bạn dùng odbc_connect (đã có dấu ?), ta dùng dấu & để nối thêm tham số
    DATABASE_URL += "&charset=utf8"

# Tạo engine kết nối CSDL
# fast_executemany=True giúp tăng tốc độ insert số lượng lớn (khuyên dùng với SQL Server)
engine = create_engine(DATABASE_URL, fast_executemany=True)

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
        # Test kết nối và thử in encoding
        with engine.connect() as conn:
            print("✅ Kết nối SQL Server thành công với UTF-8!")
            
            # (Tùy chọn) Test thử insert dữ liệu giả lập (cần bảng thật để chạy)
            # conn.execute(text("INSERT INTO test_table (name) VALUES (N'Vui vẻ')"))
            # conn.commit()
            
    except Exception as e:
        print("❌ Lỗi kết nối:", e)