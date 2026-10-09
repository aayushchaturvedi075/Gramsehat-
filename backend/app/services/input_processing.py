"""
GramSehat Layer 2: Input Processing Service
============================================
Unifies Voice Speech-to-Text (Sarvam AI Saaras) and Document OCR (EasyOCR)
into standard importable Python functions for Layer 6 and downstream pipelines.
"""

from typing import Any, Dict, Optional

from app.services.sarvam_stt_client import (
    SarvamSTTClient,
    sarvam_stt_client,
    transcribe_audio,
)
from app.services.ocr_service import ocr_service


def extract_report_text(image_bytes: bytes) -> Dict[str, str]:
    """
    Importable Python function for Layer 6 and downstream services.
    Extracts raw and normalized text from prescription or medical report image bytes.

    Args:
        image_bytes: Binary contents of the document photo (JPEG, PNG, WebP).

    Returns:
        dict: {
            "raw_text": str,
            "cleaned_text": str
        }
    """
    raw_text, cleaned_text = ocr_service.extract_text(image_bytes)
    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text
    }


__all__ = [
    "transcribe_audio",
    "extract_report_text",
    "sarvam_stt_client",
    "SarvamSTTClient"
]
