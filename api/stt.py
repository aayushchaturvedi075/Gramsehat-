import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="GramSehat Sarvam STT Serverless Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SARVAM_BASE_URL = os.environ.get("SARVAM_BASE_URL", "https://api.sarvam.ai")
SARVAM_STT_MODEL = os.environ.get("SARVAM_STT_MODEL", "saaras:v3")


async def handle_stt(
    file: UploadFile = File(...),
    language_code: str = Form("hi-IN"),
    model: str = Form(SARVAM_STT_MODEL)
):
    api_key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SARVAM_API_KEY environment variable is not configured on the server."
        )

    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Received empty or invalid audio recording."
        )

    # Sanitize content_type to remove codec parameters like ;codecs=opus which cause Sarvam HTTP 400
    cleaned_type = (file.content_type or "audio/webm").split(";")[0].strip().lower()
    filename = file.filename or "recording.webm"
    if "webm" in cleaned_type:
        content_type = "audio/webm"
        if not filename.endswith(".webm"):
            filename = f"{filename.rsplit('.', 1)[0]}.webm"
    elif "wav" in cleaned_type:
        content_type = "audio/wav"
        if not filename.endswith(".wav"):
            filename = f"{filename.rsplit('.', 1)[0]}.wav"
    elif "mp4" in cleaned_type or "m4a" in cleaned_type:
        content_type = "audio/mp4"
        if not filename.endswith(".mp4"):
            filename = f"{filename.rsplit('.', 1)[0]}.mp4"
    else:
        content_type = cleaned_type

    try:
        url = f"{SARVAM_BASE_URL.rstrip('/')}/speech-to-text"
        headers = {
            "api-subscription-key": api_key
        }
        files = {
            "file": (filename, audio_bytes, content_type)
        }
        data = {
            "model": model or SARVAM_STT_MODEL,
            "language_code": language_code or "hi-IN"
        }

        response = requests.post(url, headers=headers, files=files, data=data, timeout=40)

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
                detail=f"Sarvam AI STT error: {response.text}"
            )

        resp_data = response.json()
        transcript = resp_data.get("transcript", "")
        detected_lang = resp_data.get("language_code", language_code)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "transcript": transcript,
                "language_code": detected_lang
            }
        )
    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Sarvam AI speech recognition service timed out."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with Sarvam AI: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"STT processing failed: {str(e)}"
        )


@app.post("/api/stt")
@app.post("/stt")
@app.post("/")
async def stt_route(
    file: UploadFile = File(...),
    language_code: str = Form("hi-IN"),
    model: str = Form(SARVAM_STT_MODEL)
):
    return await handle_stt(file=file, language_code=language_code, model=model)
