from fastapi import FastAPI
from app.controllers.users import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EmoGarden API",
    description="API cho game giáo dục cảm xúc",
    version="1.0.0"
)

# CORS MỞ TOANG 2 LỚP (KHÔNG BAO GIỜ CHẾT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# LỚP CORS BỔ SUNG (DỰ PHÒNG)
from fastapi.responses import JSONResponse
@app.middleware("http")
async def cors_everywhere(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Allow-Credentials", "true")
    response.headers.setdefault("Access-Control-Allow-Methods", "*")
    response.headers.setdefault("Access-Control-Allow-Headers", "*")
    return response

@app.get("/", tags=["Health"])
def home():
    return {
        "message": "🚀 EmoGarden API SỐNG MƯỢT!",
        "docs": "http://localhost:8000/docs",
        "profile_test": "http://localhost:5173/src/pages/profile.html"
    }

app.include_router(user_router)

# CHẠY SERVER (BỎ COMMENT)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )