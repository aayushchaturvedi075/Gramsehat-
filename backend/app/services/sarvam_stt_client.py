"""
GramSehat Layer 2: Sarvam AI Speech-to-Text (STT) Client
========================================================
Dedicated client for Sarvam AI's Saaras speech recognition models (Saaras v3).
Supports multilingual Indian speech (Hindi, Hinglish codemix, 22 Indian languages).

Key Features:
- Clean modular design with hot-swappable model selection
- Audio validation: rejection of empty files, files > 10 MB, or duration > 30 seconds
- MIME type sanitization (stripping WebM/Opus codec parameters)
- Automatic 1-attempt retry on transient 5xx server errors or request timeouts
- 15-second strict timeout ensuring responsive demo execution
- Zero logging of sensitive API credentials
"""

import io
import logging
import struct
import time
import wave
from typing import Any, Dict, Optional, Tuple

import requests
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger("gramsehat.sarvam_stt")

# Whitelist of MIME types accepted by Sarvam AI REST STT
ALLOWED_AUDIO_MIMES = {
    "audio/mpeg", "audio/mp3", "audio/mpeg3", "audio/x-mpeg-3", "audio/x-mp3",
    "audio/wav", "audio/x-wav", "audio/wave", "audio/pcm_s16le", "audio/l16", "audio/raw",
    "application/octet-stream", "audio/aac", "audio/x-aac", "audio/aiff", "audio/x-aiff",
    "audio/ogg", "audio/opus", "audio/flac", "audio/x-flac", "audio/mp4", "audio/x-m4a",
    "audio/amr", "audio/x-ms-wma", "audio/webm", "video/webm"
}


def estimate_audio_duration(audio_bytes: bytes) -> Optional[float]:
    """
    Deterministically computes or estimates audio playback duration in seconds.
    Supports:
    1. Standard WAV via Python wave library
    2. WebM/Matroska via EBML Duration element (0x44 0x89)
    3. MP3 and other formats via mutagen
    """
    if not audio_bytes:
        return None

    # 1. Try WAV header inspection
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            if rate > 0:
                return float(frames) / float(rate)
    except Exception:
        pass

    # 2. Try WebM EBML element search (ID: 0x44 0x89 -> Segment Info Duration)
    try:
        idx = audio_bytes.find(b"\x44\x89")
        if idx != -1 and idx + 10 < len(audio_bytes):
            size_byte = audio_bytes[idx + 2]
            if size_byte == 0x84:  # 4-byte big-endian float
                dur = struct.unpack(">f", audio_bytes[idx + 3 : idx + 7])[0]
                return (dur / 1000.0) if dur > 100 else dur
            elif size_byte == 0x88:  # 8-byte big-endian float
                dur = struct.unpack(">d", audio_bytes[idx + 3 : idx + 11])[0]
                return (dur / 1000.0) if dur > 100 else dur
    except Exception:
        pass

    # 3. Try mutagen fallback
    try:
        import mutagen
        f = mutagen.File(io.BytesIO(audio_bytes))
        if f and hasattr(f, "info") and hasattr(f.info, "length") and f.info.length:
            return float(f.info.length)
    except Exception:
        pass

    return None


def sanitize_audio_metadata(
    raw_content_type: Optional[str],
    raw_filename: Optional[str]
) -> Tuple[str, str]:
    """
    Normalizes content_type and filename to comply with Sarvam AI STT requirements.
    Strips codec suffixes (e.g. 'audio/webm;codecs=opus' -> 'audio/webm').
    """
    cleaned_type = (raw_content_type or "audio/webm").split(";")[0].strip().lower()
    filename = raw_filename or "recording.webm"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"

    if cleaned_type not in ALLOWED_AUDIO_MIMES:
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

    ext_map = {
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
    target_ext = ext_map.get(cleaned_type, ".webm")
    base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
    safe_filename = f"{base_name}{target_ext}"

    return cleaned_type, safe_filename


class SarvamSTTClient:
    """
    Client for invoking Sarvam AI's Saaras Speech-to-Text API.
    Configurable model, language code, and processing mode (transcribe vs codemix).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 1
    ):
        self._api_key = (api_key or settings.SARVAM_API_KEY).strip()
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.SARVAM_STT_MODEL or "saaras:v3"
        self.timeout = timeout if timeout is not None else settings.SARVAM_STT_TIMEOUT
        self.max_retries = max_retries

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        content_type: Optional[str] = None,
        language_code: str = "hi-IN",
        mode: str = "transcribe",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes audio binary bytes to text via Sarvam AI REST API.

        Args:
            audio_bytes: Binary audio payload.
            filename: Original audio filename.
            content_type: MIME type of audio recording.
            language_code: BCP-47 language code (default 'hi-IN').
            mode: Output mode ('transcribe', 'codemix', 'translate', etc.).
            model: Sarvam STT model name (defaults to self.default_model).

        Returns:
            dict: {
                "transcribed_text": str,
                "language": str,
                "mode": str
            }
        """
        # 1. API key guard
        if not self._api_key:
            logger.error("SARVAM_API_KEY is not configured in environment.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SARVAM_API_KEY is not configured on the server. Please check .env configuration."
            )

        # 2. Payload size validation
        if not audio_bytes or len(audio_bytes) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Received empty or corrupted audio recording (less than 100 bytes)."
            )

        max_bytes = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
        if len(audio_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file size ({len(audio_bytes) / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of {settings.MAX_AUDIO_SIZE_MB} MB."
            )

        # 3. Audio duration validation (REST API supports <= 30 seconds)
        duration = estimate_audio_duration(audio_bytes)
        if duration is not None:
            logger.info("Detected audio duration: %.2f seconds (limit: %.1fs)", duration, settings.MAX_AUDIO_DURATION_SECONDS)
            if duration > (settings.MAX_AUDIO_DURATION_SECONDS + 0.5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Audio duration ({duration:.1f}s) exceeds the maximum allowed limit of "
                        f"{int(settings.MAX_AUDIO_DURATION_SECONDS)} seconds. Please submit audio recordings under 30s."
                    )
                )

        # 4. Metadata sanitization
        safe_content_type, safe_filename = sanitize_audio_metadata(content_type, filename)
        chosen_model = model or self.default_model
        endpoint_url = f"{self.base_url}/speech-to-text"

        headers = {
            "api-subscription-key": self._api_key
        }
        files = {
            "file": (safe_filename, audio_bytes, safe_content_type)
        }
        data = {
            "model": chosen_model,
            "language_code": language_code or "hi-IN",
            "mode": mode or "transcribe"
        }

        # 5. Network execution with 1-attempt retry on 5xx or timeout
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    "Sending STT request to %s (attempt %d/%d, model=%s, mode=%s, lang=%s, bytes=%d)",
                    endpoint_url, attempt + 1, self.max_retries + 1,
                    chosen_model, mode, language_code, len(audio_bytes)
                )

                response = requests.post(
                    endpoint_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=self.timeout
                )

                # Retry on 5xx server errors
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        logger.warning("Sarvam STT returned %s on attempt %d. Retrying...", response.status_code, attempt + 1)
                        time.sleep(1.0)
                        continue
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Sarvam AI speech recognition service encountered a server error ({response.status_code}): {response.text}"
                    )

                # Authentication error
                if response.status_code == 401:
                    logger.error("Sarvam AI STT authentication failed (401).")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Sarvam AI authentication failed. Invalid API subscription key."
                    )

                # Rate limiting
                if response.status_code == 429:
                    logger.warning("Sarvam AI STT rate limit exceeded (429).")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Sarvam AI rate limit exceeded. Please wait a few moments and try again."
                    )

                # Other HTTP client errors
                if not response.ok:
                    logger.error("Sarvam AI STT returned HTTP %s: %s", response.status_code, response.text)
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Sarvam AI STT error ({response.status_code}): {response.text}"
                    )

                # 6. Parse successful JSON response
                resp_json = response.json()
                transcript = resp_json.get("transcript", "").strip()
                detected_lang = resp_json.get("language_code", language_code)

                if not transcript:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="No recognizable speech detected in audio. Please speak clearly into the microphone and try again."
                    )

                logger.info("Successfully transcribed audio. Output length: %d chars, language: %s", len(transcript), detected_lang)
                return {
                    "transcribed_text": transcript,
                    "language": detected_lang,
                    "mode": mode
                }

            except HTTPException:
                raise
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning("Sarvam STT timed out after %.1fs (attempt %d). Retrying...", self.timeout, attempt + 1)
                    time.sleep(1.0)
                    continue
                logger.error("Sarvam STT request timed out after %d attempts: %s", self.max_retries + 1, e)
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"Sarvam AI speech-to-text service timed out after {self.timeout}s. Please try again with a shorter audio recording."
                )
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning("Sarvam STT connection error: %s (attempt %d). Retrying...", e, attempt + 1)
                    time.sleep(1.0)
                    continue
                logger.error("Sarvam STT connection error after %d attempts: %s", self.max_retries + 1, e)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to communicate with Sarvam AI STT service: {str(e)}"
                )
            except Exception as e:
                logger.exception("Unexpected error in Sarvam STT transcription: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Audio transcription failed: {str(e)}"
                )


# Global singleton client instance
sarvam_stt_client = SarvamSTTClient()


def transcribe_audio(
    file_bytes: bytes,
    filename: str = "audio.wav",
    content_type: Optional[str] = None,
    language_code: str = "hi-IN",
    mode: str = "transcribe",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Importable Python function for Layer 6 and other downstream services.
    Converts audio bytes into transcribed text using Sarvam AI Saaras STT.
    """
    return sarvam_stt_client.transcribe(
        audio_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
        language_code=language_code,
        mode=mode,
        model=model
    )
