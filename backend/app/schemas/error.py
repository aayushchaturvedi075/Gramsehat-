from typing import Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """Structured error response for input processing failures."""
    detail: str = Field(..., description="Human-readable explanation of why input processing failed")
    error_code: Optional[str] = Field(None, description="Granular error code for client triage (e.g. UNCLEAR_AUDIO, NO_TEXT_FOUND)")
