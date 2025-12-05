# Hướng dẫn Setup Game CV cho Nhóm (PowerShell)

## 📋 Yêu cầu Hệ thống

Kiểm tra các yêu cầu trước khi bắt đầu:

```powershell
# Kiểm tra Python
python --version

# Kiểm tra Node.js
node --version

# Kiểm tra Git
git --version
```

**Yêu cầu:**
- Python 3.8+
- Node.js 16+
- SQL Server đang chạy
- Git đã cài đặt

## 🚀 Hướng dẫn Setup từ đầu

### Bước 1: Clone Repository

```powershell
git clone <repository-url>
cd TTNM-Game
```

### Bước 2: Setup Backend

Mở PowerShell và chạy các lệnh sau:

```powershell
# Di chuyển vào thư mục backend
cd be

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations để tạo tables
alembic upgrade head

# Seed data cho Game CV (6 tình huống)
python scripts/seed_cv_scenarios.py

# Khởi động backend
uvicorn app.main:app --reload
```

**Lưu ý**: Giữ cửa sổ PowerShell này mở. Backend sẽ chạy tại: **http://localhost:8000**

**Kiểm tra Backend:**
- Mở browser, truy cập: http://localhost:8000/docs
- Test endpoint: `GET /games/cv/scenarios` → Nên trả về 6 scenarios

### Bước 3: Setup Frontend

**Mở PowerShell mới** (giữ cửa sổ backend đang chạy) và chạy:

```powershell
# Di chuyển vào thư mục frontend
cd fe

# Cài đặt dependencies
npm install

# Khởi động frontend
npm run dev
```

**Lưu ý**: Giữ cửa sổ PowerShell này mở. Frontend sẽ chạy tại: **http://localhost:5173**

### Bước 4: Tải Face-API.js Models (Tùy chọn)

**Cách 1: Tải thủ công (Khuyến nghị - nhanh hơn)**

```powershell
# Tạo thư mục models
New-Item -ItemType Directory -Path "public\models" -Force

# Sau đó tải các file từ link sau và đặt vào fe\public\models\
# https://github.com/justadudewhohacks/face-api.js/tree/master/weights
```

**Các file cần tải:**
- `tiny_face_detector_model-weights_manifest.json`
- `tiny_face_detector_model-shard1`
- `face_landmark_68_model-weights_manifest.json`
- `face_landmark_68_model-shard1`
- `face_recognition_model-weights_manifest.json`
- `face_recognition_model-shard1`
- `face_recognition_model-shard2`
- `face_expression_model-weights_manifest.json`
- `face_expression_model-shard1`

**Cách 2: Dùng CDN (Tự động - chậm hơn)**

Không cần làm gì, game sẽ tự động tải từ CDN khi không tìm thấy models local.

### Bước 5: Kiểm tra Setup

1. **Kiểm tra Backend**: http://localhost:8000/docs
2. **Kiểm tra Frontend**: http://localhost:5173
3. **Test Game CV**:
   - Đăng nhập tại: http://localhost:5173/src/pages/login.html
   - Chọn "Chơi game" → "Biểu Cảm Theo Tình Huống" (GV1)
   - Chọn Level 1 → Bấm "Bắt đầu Game"
   - Game sẽ hiển thị các scenarios của level 1

## 🔄 Quy trình Pull Code và Chạy

### Khi Pull Code mới từ Repository

```powershell
# 1. Pull code mới
git pull origin <branch-name>

# 2. Backend - Mở PowerShell mới
cd be
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_cv_scenarios.py
uvicorn app.main:app --reload

# 3. Frontend - Mở PowerShell mới khác
cd fe
npm install
npm run dev
```

## 🎮 Cách Chơi Game

1. **Đăng nhập**: http://localhost:5173/src/pages/login.html
2. **Chọn game**: "Chơi game" → "Biểu Cảm Theo Tình Huống" (GV1)
3. **Chọn level**: Chọn level (1-8) → Bấm "Bắt đầu Game"
4. **Đọc tình huống**: Game hiển thị tình huống (chỉ scenarios của level đã chọn)
5. **Xem gợi ý** (tùy chọn): Bấm "Gợi ý" để xem animation cảm xúc
6. **Bắt đầu**: Bấm "Bắt đầu" → Cho phép quyền camera
7. **Thể hiện cảm xúc**: Thể hiện cảm xúc theo yêu cầu
8. **Giữ cảm xúc**: Giữ đúng cảm xúc trong 2 giây để thành công
9. **Chuyển tiếp**: Tự động chuyển sang tình huống tiếp theo (cùng level)

## 🔧 Troubleshooting

### Lỗi: Backend không chạy

```powershell
# Kiểm tra Python version
python --version

# Kiểm tra dependencies đã cài chưa
pip list

# Cài lại dependencies nếu cần
pip install -r requirements.txt --force-reinstall

# Kiểm tra migrations
cd be
alembic current

# Chạy lại migrations
alembic upgrade head
```

### Lỗi: Frontend không chạy

```powershell
# Kiểm tra Node.js version
node --version

# Xóa và cài lại dependencies
cd fe
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
```

### Lỗi: Database connection

```powershell
# Kiểm tra migrations
cd be
alembic current

# Chạy lại migrations
alembic upgrade head

# Seed lại data
python scripts/seed_cv_scenarios.py
```

### Lỗi: Models Face-API.js không tải

```powershell
# Kiểm tra thư mục models
cd fe
Test-Path "public\models"

# Kiểm tra số lượng files
(Get-ChildItem "public\models" -ErrorAction SilentlyContinue).Count

# Nếu không có, tạo thư mục và tải models
New-Item -ItemType Directory -Path "public\models" -Force
# Sau đó tải các file từ GitHub và đặt vào thư mục này
```

### Lỗi: Camera không hoạt động

- Cho phép quyền camera trong browser settings
- Kiểm tra camera có đang được dùng bởi app khác không
- Thử browser khác (Chrome/Edge khuyến nghị)

### Lỗi: npm install thất bại

```powershell
# Kiểm tra Node.js version
node --version

# Xóa và cài lại
cd fe
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install

# Hoặc dùng legacy peer deps
npm install --legacy-peer-deps
```

### Lỗi: pip install thất bại

```powershell
# Kiểm tra Python version
python --version

# Tạo virtual environment (khuyến nghị)
cd be
python -m venv venv
.\venv\Scripts\Activate.ps1

# Cài dependencies trong venv
pip install -r requirements.txt
```

## 📝 Lưu ý Quan trọng

1. **Luôn chạy Backend trước Frontend**: Frontend cần backend để lấy data
2. **Giữ 2 cửa sổ PowerShell mở**: 
   - Cửa sổ 1: Backend (`uvicorn app.main:app --reload`)
   - Cửa sổ 2: Frontend (`npm run dev`)
3. **Database phải được setup trước**: Chạy migrations và seed data
4. **Models Face-API.js**: Cần tải hoặc có internet để tải từ CDN
5. **Camera Permission**: Cần cho phép quyền camera trong browser

## ✅ Checklist Setup

Chạy các lệnh sau để kiểm tra:

```powershell
# Kiểm tra Python
python --version

# Kiểm tra Node.js
node --version

# Kiểm tra Backend đang chạy
Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing

# Kiểm tra Frontend đang chạy
Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing

# Kiểm tra models đã tải chưa
Test-Path "fe\public\models"
```

## 🆘 Cần Giúp đỡ?

Nếu gặp vấn đề:

1. **Kiểm tra Console Browser**: Mở F12 → Tab Console → Xem lỗi
2. **Kiểm tra Logs Backend**: Xem cửa sổ PowerShell chạy backend
3. **Kiểm tra Logs Frontend**: Xem cửa sổ PowerShell chạy frontend
4. **Xem lại các bước setup** ở trên
5. **Liên hệ team leader** nếu vẫn không giải quyết được

## 📋 Tóm tắt Lệnh Setup Nhanh

**Backend (PowerShell 1):**
```powershell
cd be
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_cv_scenarios.py
uvicorn app.main:app --reload
```

**Frontend (PowerShell 2):**
```powershell
cd fe
npm install
npm run dev
```

**Kiểm tra:**
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Game: http://localhost:5173/src/pages/login.html

Chúc bạn setup thành công! 🎉
