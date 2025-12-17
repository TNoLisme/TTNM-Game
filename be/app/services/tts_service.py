import os
import httpx
from fastapi import HTTPException

FPT_TTS_URL = "https://api.fpt.ai/hmi/tts/v5"
FPT_API_KEY = os.getenv("FPT_API_KEY")  # lấy từ .env / env

async def fpt_tts(text: str, voice: str = "banmai", speed: float = 0):
    if not FPT_API_KEY:
        raise RuntimeError("Missing FPT_API_KEY")

    headers = {
        "api_key": FPT_API_KEY,   # chú ý: docs dùng api_key (không phải api-key)
        "voice": voice,
        "speed": str(speed),
        "Cache-Control": "no-cache",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(FPT_TTS_URL, headers=headers, content=text.encode("utf-8"))

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()

    audio_url = data.get("async")  
    if not audio_url:
        raise HTTPException(status_code=500, detail=f"Unexpected FPT response: {data}")

    return {"audioUrl": audio_url}
