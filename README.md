# TTNM Game - Ứng dụng Giáo dục Cảm xúc cho Trẻ em

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)
![Vite](https://img.shields.io/badge/Frontend-Vite-purple.svg)
![Face-API](https://img.shields.io/badge/AI-Face--API.js-red.svg)

## 📝 Giới thiệu Dự án

**TTNM Game** là một ứng dụng giáo dục tương tác được thiết kế để hỗ trợ trẻ em nhận biết và rèn luyện các biểu cảm cảm xúc. Thông qua các tình huống thực tế và công nghệ nhận diện khuôn mặt (Computer Vision), ứng dụng giúp trẻ hiểu sâu hơn về thế giới cảm xúc của chính mình và người xung quanh.

Dự án được xây dựng với cấu trúc Client-Server hiện đại, sử dụng AI để đánh giá biểu cảm của người dùng trong thời gian thực.

---

## 🚀 Tính năng Chính

- **Nhận diện cảm xúc thời gian thực**: Sử dụng Camera và Face-API.js để phân tích biểu cảm (vui, buồn, tức giận, ngạc nhiên,...).
- **Hệ thống Game đa dạng**:
    - **Biểu cảm theo tình huống (CV Game)**: Trẻ thực hiện biểu cảm dựa trên các kịch bản xã hội.
    - **Trò chơi tương tác**: Các game click và chọn lựa để học về khái niệm cảm xúc.
- **Hệ thống Level**: 8 cấp độ từ dễ đến khó với các kịch bản phong phú.
- **Quản lý & Báo cáo**:
    - Hệ thống Admin quản lý người dùng và nội dung game.
    - Xuất báo cáo tiến độ (PDF) cho phụ huynh/giáo viên.
- **Tích hợp AI (Gemini)**: Hỗ trợ phân tích và gợi ý nội dung thông minh.

---

## 🛠️ Công nghệ Sử dụng

### Backend (BE)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.8+)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: SQL Server (kết nối qua `pyodbc`)
- **Migration**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI Integration**: Google Generative AI (Gemini)
- **Tiện ích**: ReportLab (tạo PDF), Pillow (xử lý ảnh).

### Frontend (FE)
- **Tooling**: [Vite](https://vitejs.dev/)
- **Language**: Vanilla JavaScript / ES6 Modules
- **AI Library**: [Face-API.js](https://github.com/justadudewhohacks/face-api.js/)
- **Styling**: Vanilla CSS (Custom UI/UX cho trẻ em)

---

## 📁 Cấu trúc Dự án

```text
TTNM-Game/
├── be/                     # Backend Source Code (Python)
│   ├── alembic/            # Cấu hình & lịch sử database migrations
│   ├── app/                # Logic chính của ứng dụng
│   │   ├── controllers/    # API Endpoints (Routes)
│   │   ├── domain/         # Business Logic & Entities
│   │   ├── models/         # SQLAlchemy Models
│   │   ├── repository/     # Lớp tương tác Database
│   │   ├── schemas/        # Pydantic Schemas (Validation)
│   │   └── services/       # Xử lý logic phức tạp
│   ├── scripts/            # Scripts khởi tạo dữ liệu (Seed data)
│   ├── requirements.txt    # Danh sách thư viện Python
│   └── main.py             # Điểm khởi chạy Backend
├── fe/                     # Frontend Source Code (Vite + JS)
│   ├── public/             # Tài sản tĩnh & Face-API Models
│   ├── src/
│   │   ├── components/     # Các module xử lý logic JS
│   │   ├── pages/          # Giao diện HTML của ứng dụng
│   │   └── styles/         # CSS cho từng trang
│   └── vite.config.js      # Cấu hình Vite
├── run_prj.bat             # Script chạy nhanh toàn bộ project
└── structure.txt           # Chi tiết cấu trúc file hệ thống
```

---

## ⚙️ Hướng dẫn Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.8+
- Node.js 16+
- SQL Server

### 2. Setup Backend
```powershell
cd be
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_cv_scenarios.py
uvicorn app.main:app --reload
```
*Backend chạy tại: `http://localhost:8000`*

### 3. Setup Frontend
```powershell
cd fe
npm install
npm run dev
```
*Frontend chạy tại: `http://localhost:5173`*

### 4. Tải AI Models
Tải các trọng số (weights) của Face-API.js và đặt vào thư mục `fe/public/models/` để tính năng nhận diện khuôn mặt hoạt động offline.

---

## 👥 Thành viên Phát triển
- **Dự án**: Game Giáo dục Tâm lý học Trẻ em (TTNM)
- **Môi trường**: Mobile App / Web App Responsive

---
*© 2026 TTNM Game Team. All rights reserved.*
