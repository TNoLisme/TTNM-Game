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

app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    # Sử dụng host="127.0.0.1" thay vì "0.0.0.1" (địa chỉ không hợp lệ)
    uvicorn.run(app, host="localhost", port=8000, reload=True) 