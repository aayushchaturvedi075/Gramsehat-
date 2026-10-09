import os
import base64
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="GramSehat Sarvam TTS Serverless Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SARVAM_BASE_URL = os.environ.get("SARVAM_BASE_URL", "https://api.sarvam.ai")
SARVAM_TTS_MODEL = os.environ.get("SARVAM_TTS_MODEL", "bulbul:v3")
SARVAM_DEFAULT_SPEAKER = os.environ.get("SARVAM_DEFAULT_SPEAKER", "shubh")


class TTSRequest(BaseModel):
    text: str = Field(..., max_length=2500, description="Text to synthesize (max 2500 characters)")
    target_language_code: str = Field("hi-IN", description="Language code (e.g., 'hi-IN', 'en-IN')")
    speaker: Optional[str] = Field(None, description="Speaker voice identifier ('shubh', 'priya', 'kavya')")
    model: Optional[str] = Field(None, description="TTS model (defaults to bulbul:v3)")


async def handle_tts(req: TTSRequest):
    api_key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SARVAM_API_KEY environment variable is not configured on the server."
        )

    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to synthesize cannot be empty."
        )

    if len(clean_text) > 2500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text length ({len(clean_text)}) exceeds Sarvam maximum limit of 2500 characters."
        )

    try:
        url = f"{SARVAM_BASE_URL.rstrip('/')}/text-to-speech"
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": clean_text,
            "target_language_code": req.target_language_code or "hi-IN",
            "speaker": req.speaker or SARVAM_DEFAULT_SPEAKER,
            "model": req.model or SARVAM_TTS_MODEL
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sarvam AI authentication failed. Invalid API subscription key."
            )
        elif response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Sarvam AI rate limit exceeded. Please try again in a few moments."
            )
        elif not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Sarvam AI TTS error: {response.text}"
            )

        resp_data = response.json()
        audios = resp_data.get("audios", [])
        if not audios or not audios[0]:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Sarvam AI did not return any audio data."
            )

        audio_bytes = base64.b64decode(audios[0])
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Type": "audio/wav",
                "Content-Disposition": "inline; filename=\"speech.wav\"",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Sarvam AI text-to-speech service timed out."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with Sarvam AI: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS synthesis failed: {str(e)}"
        )


@app.post("/api/tts")
@app.post("/tts")
@app.post("/")
async def tts_route(req: TTSRequest):
    return await handle_tts(req)
