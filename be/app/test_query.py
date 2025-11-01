import sys
sys.path.append('app')  # Thêm path để import từ app

from app.database import get_db
from app.repository.users_repo import UsersRepository
from sqlalchemy.orm import Session

db = next(get_db())
repo = UsersRepository(db)
email = "acctanzz1@gmail.com"  # Email mày test

user = repo.get_by_email(email)
if user:
    print("User found:", user.email, user.username)  # In email & username nếu tìm thấy
else:
    print("Email not found in DB")
db.close()