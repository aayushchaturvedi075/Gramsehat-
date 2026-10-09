import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import triage_router, ocr_router, reasoning_router, sarvam_router, rules_router
from app.services import ocr_service

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("gramsehat.backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager: loads EasyOCR model ONCE at startup.
    Voice STT and TTS are processed natively in the client browser via Web Speech API,
    with final transcripts sent directly to the /process-transcript endpoint.
    """
    logger.info("Initializing GramSehat Backend...")

    # Preload EasyOCR model
    try:
        ocr_service.load_model()
    except Exception as e:
        logger.critical("Failed to load EasyOCR on startup: %s", e)
        raise

    logger.info("AI models initialized. Ready to process transcripts and medical reports.")
    
    yield
    
    logger.info("Shutting down GramSehat Backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "GramSehat Clinical Backend.\n\n"
        "- High-accuracy Indian voice STT (Saaras v3) and TTS (Bulbul v3) powered by Sarvam AI.\n"
        "- Extracts text from doctor prescriptions and lab reports using EasyOCR (English + Hindi).\n"
        "- Layer 4 AI Reasoning powered by Sarvam AI LLMs (Sarvam-30B & Sarvam-105B) for symptom structuring, report explanations, and hospital handover summaries."
    ),
    lifespan=lifespan
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["System"],
    summary="Health check and service status"
)
async def health_check():
    """Health check endpoint indicating model readiness and service status."""
    return {
        "status": "healthy",
        "service": "GramSehat Backend",
        "voice_pipeline": {
            "provider": "Sarvam AI",
            "stt": f"Sarvam Speech-to-Text ({settings.SARVAM_STT_MODEL})",
            "tts": f"Sarvam Text-to-Speech ({settings.SARVAM_TTS_MODEL})",
            "default_speaker": settings.SARVAM_DEFAULT_SPEAKER,
            "proxy_endpoints": ["/api/stt", "/api/tts"]
        },
        "layer4_ai_reasoning": {
            "status": "active",
            "provider": "Sarvam AI (OpenAI-compatible API)",
            "models": {
                "symptom_structuring": settings.SARVAM_MODEL_SYMPTOM_STRUCTURING,
                "report_explanation": settings.SARVAM_MODEL_REPORT_EXPLANATION,
                "hospital_summary": settings.SARVAM_MODEL_HOSPITAL_SUMMARY,
                "fallback": settings.SARVAM_MODEL_FALLBACK
            },
            "retry_policy": f"{settings.SARVAM_MAX_RETRIES} retry"
        },
        "models": {
            "easyocr": {
                "loaded": ocr_service.is_loaded(),
                "languages": settings.OCR_LANGUAGES
            }
        }
    }


# Include routers
app.include_router(triage_router)
app.include_router(ocr_router)
app.include_router(reasoning_router)
app.include_router(sarvam_router)
app.include_router(rules_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback global exception handler to guarantee clean, structured error responses."""
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"An internal server error occurred: {str(exc)}",
            "error_type": exc.__class__.__name__
        }
    )
