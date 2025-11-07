import sys
sys.path.append('app')  # Thêm path

from app.database import get_db
from app.repository.users_repo import UsersRepository
from sqlalchemy.orm import Session

# Kết nối DB
db: Session = next(get_db())
repo = UsersRepository(db)

# === THỬ LOGIN ===
username = "testuser"  # Thay nếu cần
password = "supernewpass!"  # Pass plain

print(f"Querying username: {username}")

user = repo.get_by_username(username)

if user:
    print(f"Found user: {user}")
    print(f"All attributes: {user.__dict__}")  # IN HẾT ĐỂ XEM TÊN FIELD PASS
    
    # TỰ ĐỘNG TÌM FIELD PASS (thử các tên phổ biến)
    pass_field = None
    for key in user.__dict__:
        if 'pass' in key.lower() or 'hash' in key.lower():
            pass_field = key
            break
    
    if pass_field:
        stored_pass = getattr(user, pass_field)
        print(f"Found password field: {pass_field} = {stored_pass}")
        
        if stored_pass == password:
            print("[SUCCESS] Pass đúng (plain text)!")
        else:
            print("[ERROR] Pass sai! Thử hash...")
            # Thử SHA256
            import hashlib
            if stored_pass == hashlib.sha256(password.encode()).hexdigest():
                print("[SUCCESS] Pass đúng (SHA256)!")
            else:
                print("[ERROR] Pass sai hoàn toàn!")
    else:
        print("[ERROR] Không tìm thấy field password nào!")
else:
    print("[ERROR] User không tồn tại! Tạo user test...")

    from app.domain.users.user import User  # Import model
    
    new_user = User(
        username=username,
        email="test@gmail.com",
        password=password,  # Thử field 'password' (BE sẽ hash sau)
        # hashed_password=password,  # Bỏ comment nếu field là hashed_password
        role="parent",
        fullname="Test User"
    )
    
    repo.create(new_user)
    db.commit()
    print("[SUCCESS] User 'testuser' created! Pass: supernewpass!")

db.close()
print("[DONE] Test hoàn thành!")