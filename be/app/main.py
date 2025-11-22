from fastapi import FastAPI
from app.controllers.users import user_router
from app.controllers.games.cv_controller import router as cv_router
from app.controllers.users import admin_router
from app.controllers.analytics.report_controller import router as report_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EmoGarden API",
    description="API cho game giáo dục cảm xúc",
    version="1.0.0"
)

# ✅ CORS ĐÚNG - Không dùng wildcard với credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Cho phép gửi credentials
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/", tags=["Health"])
def home():
    return {
        "message": "🚀 EmoGarden API SỐNG MƯỢT!",
        "docs": "http://localhost:8000/docs",
        "profile_test": "http://localhost:5173/src/pages/profile.html"
    }

# Include routers
app.include_router(user_router)    
app.include_router(admin_router)     
app.include_router(cv_router)   
app.include_router(report_router)    

# CHẠY SERVER
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )