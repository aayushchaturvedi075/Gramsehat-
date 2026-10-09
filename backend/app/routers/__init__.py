from .triage import router as triage_router
from .ocr import router as ocr_router
from .input_processing import router as input_processing_router
from .reasoning import router as reasoning_router
from .sarvam import router as sarvam_router
from .rules import router as rules_router

__all__ = [
    "triage_router",
    "ocr_router",
    "input_processing_router",
    "reasoning_router",
    "sarvam_router",
    "rules_router"
]
