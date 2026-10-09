"""
Layer 2 OCR router alias.
Maintained for backwards compatibility with existing imports.
Delegates to the unified input_processing router.
"""

from app.routers.input_processing import router

__all__ = ["router"]
