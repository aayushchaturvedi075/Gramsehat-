"""
Pydantic schemas for GramSehat Layer 2: Input Processing.
Defines structured responses for voice audio transcription and document OCR extraction.
"""

from pydantic import BaseModel, Field


class TranscribeAudioResponse(BaseModel):
    """
    Response schema for POST /transcribe-audio.
    Returns the transcribed text along with detected/matched language and processing mode.
    """
    transcribed_text: str = Field(
        ...,
        description="Transcribed text from patient speech",
        json_schema_extra={"example": "नमस्ते डॉक्टर साहब, मुझे दो दिनों से सीने में दर्द है।"}
    )
    language: str = Field(
        ...,
        description="Language code of the transcribed audio (e.g. 'hi-IN', 'en-IN')",
        json_schema_extra={"example": "hi-IN"}
    )
    mode: str = Field(
        ...,
        description="Mode used for transcription ('transcribe', 'codemix', 'translate', etc.)",
        json_schema_extra={"example": "transcribe"}
    )


class ExtractReportTextResponse(BaseModel):
    """
    Response schema for POST /extract-report-text.
    Returns both raw OCR lines and a normalized cleaned text representation.
    """
    raw_text: str = Field(
        ...,
        description="Exact raw text lines recognized by EasyOCR",
        json_schema_extra={"example": "BP 130/85 mmHg\nTemp 100.8 F\nTab Paracetamol 650mg"}
    )
    cleaned_text: str = Field(
        ...,
        description="Cleaned, standardized text with normalized whitespace and lines for downstream LLM reasoning",
        json_schema_extra={"example": "BP 130/85 mmHg\nTemp 100.8 F\nTab Paracetamol 650mg"}
    )
