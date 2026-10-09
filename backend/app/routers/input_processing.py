"""
FastAPI Router for GramSehat Layer 2: Input Processing.
Exposes endpoints for audio voice transcription (Sarvam AI Saaras)
and medical prescription/report OCR (EasyOCR).
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, status

from app.schemas.error import ErrorResponse
from app.schemas.input_processing import (
    ExtractReportTextResponse,
    TranscribeAudioResponse,
)
from app.services.input_processing import extract_report_text, transcribe_audio
from app.utils.file_validation import validate_image_file

logger = logging.getLogger("gramsehat.input_processing")

router = APIRouter(
    tags=["Layer 2: Input Processing (Speech & OCR)"]
)


@router.post(
    "/transcribe-audio",
    response_model=TranscribeAudioResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe patient voice audio (Sarvam AI Saaras)",
    description=(
        "Converts uploaded audio recordings (WebM, WAV, MP3, etc.) to text using Sarvam AI Saaras v3.\n\n"
        "- Default language: 'hi-IN' (Hindi), with support for 22 Indian languages or 'auto'.\n"
        "- Mode: 'transcribe' (default) or 'codemix' (for Hinglish phrasing).\n"
        "- Enforces strict duration limits (under 30 seconds) and size limits (under 10 MB).\n"
        "- Built-in automatic 1-retry on network timeout or 5xx server issues."
    ),
    responses={
        200: {
            "model": TranscribeAudioResponse,
            "description": "Audio successfully transcribed."
        },
        400: {
            "model": ErrorResponse,
            "description": "Audio too long (>30s) or invalid audio content."
        },
        413: {
            "model": ErrorResponse,
            "description": "Audio file exceeds maximum size limit (10 MB)."
        },
        422: {
            "model": ErrorResponse,
            "description": "No recognizable speech detected in audio recording."
        },
        502: {
            "model": ErrorResponse,
            "description": "Failed to communicate with Sarvam AI STT service."
        },
        504: {
            "model": ErrorResponse,
            "description": "Sarvam AI STT service timed out."
        }
    }
)
async def transcribe_audio_endpoint(
    file: UploadFile = File(..., description="Audio recording file (webm, mp3, wav, etc.)"),
    language_code: str = Form("hi-IN", description="BCP-47 language code (default: 'hi-IN')"),
    mode: str = Form("transcribe", description="Transcription mode: 'transcribe', 'codemix', 'translate', etc."),
    model: Optional[str] = Form(None, description="Sarvam STT model name (default: configured saaras:v3)")
) -> TranscribeAudioResponse:
    """
    HTTP endpoint wrapper for transcribe_audio.
    Extracts bytes and executes transcription via Sarvam AI Saaras.
    """
    logger.info(
        "Received audio transcription request: filename=%s, content_type=%s, lang=%s, mode=%s",
        file.filename, file.content_type, language_code, mode
    )

    file_bytes = await file.read()
    result = transcribe_audio(
        file_bytes=file_bytes,
        filename=file.filename or "recording.webm",
        content_type=file.content_type,
        language_code=language_code,
        mode=mode,
        model=model
    )

    return TranscribeAudioResponse(
        transcribed_text=result["transcribed_text"],
        language=result["language"],
        mode=result["mode"]
    )


@router.post(
    "/extract-report-text",
    response_model=ExtractReportTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from prescription or medical report (EasyOCR)",
    description=(
        "Extracts bilingual text (English + Hindi) from photos of prescriptions, lab reports, "
        "and clinical discharge summaries using EasyOCR.\n\n"
        "- Returns both raw OCR text and a lightly cleaned version (normalized whitespace and lines).\n"
        "- Loaded once into memory at server startup for fast execution."
    ),
    responses={
        200: {
            "model": ExtractReportTextResponse,
            "description": "Document text successfully extracted."
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid input file (e.g. empty file or missing filename)."
        },
        413: {
            "model": ErrorResponse,
            "description": "Image file exceeds maximum size limit (15 MB)."
        },
        415: {
            "model": ErrorResponse,
            "description": "Unsupported image format."
        },
        422: {
            "model": ErrorResponse,
            "description": "Image could not be decoded or contains no readable text."
        }
    }
)
async def extract_report_text_endpoint(
    file: UploadFile = File(..., description="Prescription or lab report image (jpg, png, webp)")
) -> ExtractReportTextResponse:
    """
    HTTP endpoint wrapper for extract_report_text.
    Extracts image bytes and executes EasyOCR document reading.
    """
    logger.info("Received document OCR extraction request: filename=%s", file.filename)

    file_bytes = await file.read()
    validate_image_file(file, file_bytes)

    result = extract_report_text(file_bytes)

    logger.info(
        "Successfully extracted report text (%s): raw_chars=%d, clean_chars=%d",
        file.filename, len(result["raw_text"]), len(result["cleaned_text"])
    )

    return ExtractReportTextResponse(
        raw_text=result["raw_text"],
        cleaned_text=result["cleaned_text"]
    )
