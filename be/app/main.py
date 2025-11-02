from fastapi import FastAPI
from app.controllers.users import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Thêm middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], 
    allow_headers=["*"],
)

# Gắn router người dùng
app.include_router(user_router)

# ✅ Route mặc định cho "/"
@app.get("/")
def root():
    return {"message": "Welcome to the TTNM Game API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=True)
