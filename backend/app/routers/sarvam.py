"""
Router for Sarvam AI Voice Pipeline: STT (Saaras v3) & TTS (Bulbul v3).
Acts as a secure server-side proxy so that the SARVAM_API_KEY is never exposed to the client.
"""

import base64
import logging
from typing import Optional

import requests
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sarvam Voice AI (STT & TTS)"])


class TTSRequest(BaseModel):
    """Request payload for Sarvam Text-to-Speech generation."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=2500,
        description="Text to convert to speech (max 2500 characters per request)",
        json_schema_extra={"example": "नमस्ते, ग्रामसेहत में आपका स्वागत है।"}
    )
    target_language_code: Optional[str] = Field(
        default="hi-IN",
        description="Target language code (e.g., 'hi-IN', 'en-IN')",
        json_schema_extra={"example": "hi-IN"}
    )
    speaker: Optional[str] = Field(
        default="shubh",
        description="Voice persona: 'shubh' (default), 'priya', 'kavya'",
        json_schema_extra={"example": "shubh"}
    )
    model: Optional[str] = Field(
        default="bulbul:v3",
        description="Sarvam TTS model name (default: 'bulbul:v3')",
        json_schema_extra={"example": "bulbul:v3"}
    )


class STTResponse(BaseModel):
    """Response payload for Sarvam Speech-to-Text transcription."""
    transcript: str = Field(..., description="Transcribed text from audio")
    language_code: str = Field(..., description="Detected or matched language code")


# Strict whitelist of MIME types accepted by Sarvam AI STT
SARVAM_ALLOWED_AUDIO_MIMES = {
    "audio/mpeg", "audio/mp3", "audio/mpeg3", "audio/x-mpeg-3", "audio/x-mp3",
    "audio/wav", "audio/x-wav", "audio/wave", "audio/pcm_s16le", "audio/l16", "audio/raw",
    "application/octet-stream", "audio/aac", "audio/x-aac", "audio/aiff", "audio/x-aiff",
    "audio/ogg", "audio/opus", "audio/flac", "audio/x-flac", "audio/mp4", "audio/x-m4a",
    "audio/amr", "audio/x-ms-wma", "audio/webm", "video/webm"
}


def sanitize_audio_metadata(raw_content_type: Optional[str], raw_filename: Optional[str]) -> tuple[str, str]:
    """
    Sanitizes content_type and filename to strictly match Sarvam AI STT allowed MIME list.
    Crucially strips codec parameters (e.g. 'audio/webm;codecs=opus' -> 'audio/webm')
    which cause Sarvam API to return HTTP 400.
    """
    cleaned_type = (raw_content_type or "audio/webm").split(";")[0].strip().lower()
    filename = raw_filename or "audio.webm"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"

    if cleaned_type not in SARVAM_ALLOWED_AUDIO_MIMES:
        if "webm" in cleaned_type or ext == "webm":
            cleaned_type = "audio/webm"
        elif "wav" in cleaned_type or ext == "wav":
            cleaned_type = "audio/wav"
        elif "mp4" in cleaned_type or "m4a" in cleaned_type or ext in ("mp4", "m4a"):
            cleaned_type = "audio/mp4"
        elif "ogg" in cleaned_type or "opus" in cleaned_type or ext in ("ogg", "opus"):
            cleaned_type = "audio/ogg"
        elif "mp3" in cleaned_type or "mpeg" in cleaned_type or ext == "mp3":
            cleaned_type = "audio/mp3"
        elif "flac" in cleaned_type or ext == "flac":
            cleaned_type = "audio/flac"
        elif "aac" in cleaned_type or ext == "aac":
            cleaned_type = "audio/aac"
        else:
            cleaned_type = "audio/webm"

    mime_to_ext = {
        "audio/webm": ".webm",
        "video/webm": ".webm",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/wave": ".wav",
        "audio/mp4": ".mp4",
        "audio/x-m4a": ".m4a",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/ogg": ".ogg",
        "audio/opus": ".opus",
        "audio/flac": ".flac",
        "audio/aac": ".aac",
    }
    target_ext = mime_to_ext.get(cleaned_type, ".webm")
    base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
    safe_filename = f"{base_name}{target_ext}"

    return cleaned_type, safe_filename


# Helper function for STT logic
async def _execute_stt(
    file: UploadFile,
    language_code: str = "hi-IN",
    model: str = "saaras:v3"
) -> STTResponse:
    api_key = settings.SARVAM_API_KEY
    if not api_key:
        logger.error("SARVAM_API_KEY is missing on server")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SARVAM_API_KEY environment variable is not configured on server"
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty (0 bytes received)"
        )

    # Sanitize content-type and filename so codec parameters don't cause Sarvam HTTP 400
    content_type, filename = sanitize_audio_metadata(file.content_type, file.filename)
    files = {"file": (filename, file_bytes, content_type)}
    data = {
        "model": model or settings.SARVAM_STT_MODEL,
        "language_code": language_code or "hi-IN"
    }
    headers = {"api-subscription-key": api_key}

    logger.info("Forwarding audio (%d bytes, %s as %s) to Sarvam STT [%s]", len(file_bytes), content_type, filename, data["model"])

    try:
        resp = requests.post(
            f"{settings.SARVAM_BASE_URL}/speech-to-text",
            files=files,
            data=data,
            headers=headers,
            timeout=30.0
        )
    except requests.exceptions.Timeout:
        logger.error("Sarvam STT request timed out after 30s")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Sarvam AI speech recognition service timed out. Please try again."
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Network error communicating with Sarvam AI: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to Sarvam AI STT: {str(exc)}"
        )

    if resp.status_code != 200:
        err_msg = resp.text
        try:
            err_json = resp.json()
            if isinstance(err_json.get("error"), dict):
                err_msg = err_json["error"].get("message") or str(err_json["error"])
            else:
                err_msg = err_json.get("message") or err_json.get("error") or resp.text
        except Exception:
            pass

        logger.warning("Sarvam STT returned error HTTP %d: %s", resp.status_code, err_msg)
        if resp.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or unauthorized SARVAM_API_KEY"
            )
        elif resp.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Sarvam AI rate limit exceeded. Please wait a moment."
            )
        else:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Sarvam STT error ({resp.status_code}): {err_msg}"
            )

    result_json = resp.json()
    transcript = result_json.get("transcript", "").strip()
    returned_lang = result_json.get("language_code", language_code)

    logger.info("Sarvam STT successfully transcribed: '%s' (lang: %s)", transcript, returned_lang)
    return STTResponse(transcript=transcript, language_code=returned_lang)


# Helper function for TTS logic
async def _execute_tts(payload: TTSRequest) -> Response:
    api_key = settings.SARVAM_API_KEY
    if not api_key:
        logger.error("SARVAM_API_KEY is missing on server")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SARVAM_API_KEY environment variable is not configured on server"
        )

    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text for speech synthesis cannot be empty"
        )

    # Sarvam Bulbul v3 supports max 2500 characters per request
    text_chunk = clean_text[:2500]

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    sarvam_data = {
        "text": text_chunk,
        "target_language_code": payload.target_language_code or "hi-IN",
        "speaker": payload.speaker or settings.SARVAM_DEFAULT_SPEAKER,
        "model": payload.model or settings.SARVAM_TTS_MODEL
    }

    logger.info(
        "Requesting Sarvam TTS [model: %s, speaker: %s, lang: %s] for text length: %d chars",
        sarvam_data["model"], sarvam_data["speaker"], sarvam_data["target_language_code"], len(text_chunk)
    )

    try:
        resp = requests.post(
            f"{settings.SARVAM_BASE_URL}/text-to-speech",
            json=sarvam_data,
            headers=headers,
            timeout=25.0
        )
    except requests.exceptions.Timeout:
        logger.error("Sarvam TTS request timed out after 25s")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Sarvam AI speech synthesis service timed out. Please try again."
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Network error communicating with Sarvam AI TTS: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to Sarvam AI TTS: {str(exc)}"
        )

    if resp.status_code != 200:
        err_msg = resp.text
        try:
            err_json = resp.json()
            if isinstance(err_json.get("error"), dict):
                err_msg = err_json["error"].get("message") or str(err_json["error"])
            else:
                err_msg = err_json.get("message") or err_json.get("error") or resp.text
        except Exception:
            pass

        logger.warning("Sarvam TTS returned error HTTP %d: %s", resp.status_code, err_msg)
        if resp.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or unauthorized SARVAM_API_KEY"
            )
        elif resp.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Sarvam AI rate limit exceeded. Please wait a moment."
            )
        else:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Sarvam TTS error ({resp.status_code}): {err_msg}"
            )

    result_json = resp.json()
    audios = result_json.get("audios", [])
    if not audios or not audios[0]:
        logger.error("Sarvam TTS response missing audios array")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sarvam AI returned an empty audio array"
        )

    # Decode base64 audio to raw WAV bytes
    try:
        audio_bytes = base64.b64decode(audios[0])
    except Exception as exc:
        logger.error("Failed to decode base64 audio from Sarvam TTS: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decode generated audio data"
        )

    logger.info("Successfully decoded Sarvam TTS audio: %d bytes (WAV)", len(audio_bytes))
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Content-Type": "audio/wav",
            "Content-Disposition": 'inline; filename="sarvam_speech.wav"',
            "Cache-Control": "public, max-age=3600"
        }
    )


# Route definitions supporting both /api/stt and /stt, /api/tts and /tts
@router.post("/api/stt", response_model=STTResponse, summary="Sarvam Speech-to-Text Proxy (Saaras v3)")
@router.post("/stt", response_model=STTResponse, summary="Sarvam Speech-to-Text Proxy Alias")
async def speech_to_text(
    file: UploadFile = File(...),
    language_code: str = Form("hi-IN"),
    model: str = Form("saaras:v3")
):
    """Forwards audio clip to Sarvam STT REST API and returns transcribed text."""
    return await _execute_stt(file, language_code, model)


@router.post("/api/tts", summary="Sarvam Text-to-Speech Proxy (Bulbul v3)")
@router.post("/tts", summary="Sarvam Text-to-Speech Proxy Alias")
async def text_to_speech(payload: TTSRequest):
    """Converts text to natural Indian speech using Sarvam Bulbul v3, returning decoded WAV audio."""
    return await _execute_tts(payload)
