@echo off
title RUN TTNM-GAME PROJECT
echo ==============================
echo  🚀 BẮT ĐẦU KHỞI CHẠY DỰ ÁN TTNM-GAME
echo ==============================

:: Di chuyển đến thư mục dự án gốc
cd /d E:\code\TTNM\copy\TTNM-Game

:: --- GIT CHECKOUT BRANCH ---
echo.
echo ==== CHUYỂN SANG NHÁNH user/thinh ====
git checkout user/thinh

:: --- BACKEND SETUP ---
echo.
echo ==== CÀI ĐẶT BACKEND ====
cd be

:: Tạo file .env (nếu chưa tồn tại)
if not exist .env (
    echo Tạo file .env ...
    (
        echo # ---- DATABASE CONFIG ----
        echo DATABASE_URL_SQLSERVER=mssql+pyodbc:///?odbc_connect=DRIVER%%3D%%7BODBC+Driver+17+for+SQL+Server%%7D%%3BSERVER%%3Dlocalhost%%5CTHINHSQL%%3BDATABASE%%3DTTNM%%3BUID%%3Dsa%%3BPWD%%3DyuiyL23021726
        echo.
        echo # ---- APP CONFIG ----
        echo APP_NAME=FastAPI Backend
        echo APP_ENV=development
    ) > .env
)

echo.
echo Cài đặt thư viện Python...
pip install -r requirements.txt

:: Chạy server backend trong cửa sổ mới
echo.
echo ==== KHỞI ĐỘNG BACKEND ====
start cmd /k "uvicorn app.main:app --reload"


echo ===== CÀI ĐẶT FRONTEND =====
cd fe
echo Đang xóa cache và node_modules...
rmdir /s /q node_modules
del /f /q package-lock.json
call npm cache clean --force

echo Đang cài các thư viện FE...
call npm install
call npm install vite rollup --save-dev

echo ===== KHỞI CHẠY FRONTEND =====
start cmd /k "cd /d %cd% && call npm run dev"
