import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory or workspace root
_base_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(_base_dir / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv()

class Settings:
    """Configuration settings for GramSehat Backend Module."""
    
    PROJECT_NAME: str = "GramSehat - Clinical AI & OCR Processing"
    VERSION: str = "2.1.0"
    API_V1_STR: str = ""
    
    # Sarvam AI Voice Pipeline Configuration
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_BASE_URL: str = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
    SARVAM_STT_MODEL: str = os.getenv("SARVAM_STT_MODEL", "saaras:v3")
    SARVAM_STT_TIMEOUT: float = float(os.getenv("SARVAM_STT_TIMEOUT", "15.0"))
    MAX_AUDIO_SIZE_MB: int = int(os.getenv("MAX_AUDIO_SIZE_MB", "10"))
    MAX_AUDIO_DURATION_SECONDS: float = float(os.getenv("MAX_AUDIO_DURATION_SECONDS", "30.0"))
    SARVAM_TTS_MODEL: str = os.getenv("SARVAM_TTS_MODEL", "bulbul:v3")
    SARVAM_DEFAULT_SPEAKER: str = os.getenv("SARVAM_DEFAULT_SPEAKER", "shubh")
    
    # EasyOCR Configuration
    # Supports bilingual extraction (Hindi Devanagari + English) for prescriptions and lab reports
    OCR_LANGUAGES: list = ["en", "hi"]
    OCR_GPU: bool = os.getenv("OCR_GPU", "false").lower() == "true"
    
    # Upload limits & constraints for report/prescription images
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "15"))
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
    ALLOWED_IMAGE_MIMES: set = {
        "image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"
    }

    # Layer 4: Sarvam AI Reasoning Configuration (OpenAI-compatible)
    SARVAM_REASONING_BASE_URL: str = os.getenv("SARVAM_REASONING_BASE_URL", "https://api.sarvam.ai/v1")
    # Speed-critical: Live conversational symptom structuring (Sarvam-105B)
    SARVAM_MODEL_SYMPTOM_STRUCTURING: str = os.getenv("SARVAM_MODEL_SYMPTOM_STRUCTURING", "sarvam-105b-conversations")
    # Accuracy-critical: Patient lab/prescription explanation (Sarvam-105B)
    SARVAM_MODEL_REPORT_EXPLANATION: str = os.getenv("SARVAM_MODEL_REPORT_EXPLANATION", "sarvam-105b-conversations")
    # Accuracy-critical: Clinical SBAR hospital handover summary (Sarvam-105B)
    SARVAM_MODEL_HOSPITAL_SUMMARY: str = os.getenv("SARVAM_MODEL_HOSPITAL_SUMMARY", "sarvam-105b-conversations")
    # Fallback model for retired or unavailable model endpoints
    SARVAM_MODEL_FALLBACK: str = os.getenv("SARVAM_MODEL_FALLBACK", "sarvam-105b-conversations")
    
    # Retry policy: 1 retry for API timeout, rate limits, or malformed JSON
    SARVAM_MAX_RETRIES: int = int(os.getenv("SARVAM_MAX_RETRIES", "1"))
    SARVAM_REQUEST_TIMEOUT: float = float(os.getenv("SARVAM_REQUEST_TIMEOUT", "30.0"))

    # Legacy/Fallback Gemini Configuration (kept for optional multi-provider testing)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_SYMPTOM_STRUCTURING: str = os.getenv("MODEL_SYMPTOM_STRUCTURING", "sarvam-30b")
    MODEL_REPORT_EXPLANATION: str = os.getenv("MODEL_REPORT_EXPLANATION", "sarvam-105b-conversations")
    MODEL_HOSPITAL_SUMMARY: str = os.getenv("MODEL_HOSPITAL_SUMMARY", "sarvam-105b-conversations")
    MODEL_FALLBACK_FLASH: str = os.getenv("MODEL_FALLBACK_FLASH", "sarvam-105b-conversations")
    MODEL_FALLBACK_PRO: str = os.getenv("MODEL_FALLBACK_PRO", "sarvam-105b-conversations")
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "1"))
    GEMINI_REQUEST_TIMEOUT: float = float(os.getenv("GEMINI_REQUEST_TIMEOUT", "20.0"))

settings = Settings()
