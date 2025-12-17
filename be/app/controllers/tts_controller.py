from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tts_service import fpt_tts

router = APIRouter(prefix="/tts", tags=["tts"])

class TTSReq(BaseModel):
    text: str
    voice: str | None = "banmai"
    speed: float | None = 0

@router.post("")
async def tts(req: TTSReq):
    return await fpt_tts(
        text=req.text,
        voice=req.voice or "banmai",
        speed=req.speed if req.speed is not None else 0,
    )
