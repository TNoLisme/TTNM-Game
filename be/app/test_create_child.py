# be/app/test_create_child.py – DÁN ĐÈ TOÀN BỘ
import sys
sys.path.append('app')
from app.database import get_db
from app.services.users.users_service import UsersService
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository

db = next(get_db())
service = UsersService(UsersRepository(db), ChildRepository(db))

result = service.create_child({
    "username": "testchild2",          # Username mới
    "email": "child2@test.com",        # Email mới
    "password": "12345678",
    "name": "Child Test 2",
    "age": 8,
    "gender": "male",
    "phone_number": "0999999999",      # PHONE MỚI, KHÔNG TRÙNG!
    "date_of_birth": "2017-01-01",
    "report_preferences": "weekly",
    "role": "child"
})
print("CREATE CHILD RESULT:", result)

# IN RA USER_ID ĐỂ DÙNG SAU
if result.get("status") == "success":
    user_id = result.get("user_id")
    print(f"[SUCCESS] Child created! User ID: {user_id}")
    print("Copy user_id này vào test_profile.py")
else:
    print("[ERROR] Tạo thất bại!")

db.close()