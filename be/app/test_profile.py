import sys
sys.path.append('app')  # Thêm path để import

from app.database import get_db
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.services.users.users_service import UsersService
from uuid import UUID
from sqlalchemy.orm import Session

# Kết nối DB
db: Session = next(get_db())
user_repo = UsersRepository(db)
child_repo = ChildRepository(db)
service = UsersService(user_repo, child_repo)

# === USER ID TEST (thay bằng user_id thật từ DB, ví dụ từ test_login.py) ===
# DÁN ĐÈ DÒNG NÀY TRONG test_profile.py
user_id = UUID("ab522c90-c812-4459-8eb4-0af23bd0414d")  # USER_ID MỚI TỪ MÀY

print(f"[TEST] Bắt đầu test profile cho user_id: {user_id}")

# TEST 1: GET PROFILE (lấy info hiện tại)
print("\n[1] GET PROFILE:")
profile = service.get_current_user_info(user_id)
if profile:
    print("PROFILE HIỆN TẠI:")
    for k, v in profile.items():
        print(f"  {k}: {v}")
else:
    print("[ERROR] Không lấy được profile!")

# TEST 2: UPDATE PROFILE (sửa user + child nếu có)
print("\n[2] UPDATE PROFILE:")
update_data = {
    "name": "Test User Updated",      # Sửa name user
    "phone_number": "0987654321",     # Sửa phone child
    "age": 12                         # Sửa age child (nếu là child)
}
result = service.update_profile(user_id, update_data)
print("UPDATE RESULT:", result)

# TEST 3: GET PROFILE SAU UPDATE (kiểm tra thay đổi)
print("\n[3] GET PROFILE SAU UPDATE:")
new_profile = service.get_current_user_info(user_id)
if new_profile:
    print("PROFILE MỚI:")
    for k, v in new_profile.items():
        print(f"  {k}: {v}")
else:
    print("[ERROR] Không lấy được profile sau update!")

# TEST CHILD RIÊNG (nếu cần)
print("\n[4] TEST CHILD REPO RIÊNG:")
child = child_repo.get_by_user_id(user_id)
if child:
    print("CHILD HIỆN TẠI:", child.__dict__)
    
    # Sửa child trực tiếp
    child.phone_number = "0999999999"
    child.age = 15
    updated_child = child_repo.update(child)
    print("CHILD UPDATED:", updated_child.__dict__)
else:
    print("[INFO] Không phải child hoặc không có child info.")

db.close()
print("\n[DONE] Test profile hoàn thành! Kiểm tra DB thay đổi.")