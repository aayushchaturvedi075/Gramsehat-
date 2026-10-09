import io
import logging
from typing import Tuple
import numpy as np
from PIL import Image
from fastapi import HTTPException, status
from app.config import settings
from app.utils.text_cleaning import clean_ocr_text

logger = logging.getLogger(__name__)


class EasyOCRService:
    """
    Singleton service for Optical Character Recognition (OCR) using EasyOCR.
    Initialized with English ('en') and Hindi ('hi') language models for rural
    prescriptions and laboratory reports.
    
    Loads the model once at startup to keep per-request latency minimal.
    """

    def __init__(self) -> None:
        self.reader = None
        self.languages = settings.OCR_LANGUAGES
        self.gpu = settings.OCR_GPU

    def load_model(self) -> None:
        """Loads the EasyOCR Reader models into memory. Called once during application lifespan startup."""
        if self.reader is None:
            logger.info("Initializing EasyOCR Reader for languages: %s (GPU=%s)...", self.languages, self.gpu)
            try:
                import easyocr
                self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
                logger.info("EasyOCR Reader successfully initialized.")
            except Exception as e:
                logger.error("Failed to initialize EasyOCR Reader: %s", e)
                raise RuntimeError(f"Failed to initialize EasyOCR: {e}") from e

    def is_loaded(self) -> bool:
        return self.reader is not None

    def extract_text(self, image_bytes: bytes) -> Tuple[str, str]:
        """
        Extracts raw and cleaned text from image bytes.
        
        Args:
            image_bytes: Raw binary content of the prescription or lab report image.
            
        Returns:
            Tuple of (raw_text, cleaned_text)
            
        Raises:
            HTTPException: If image cannot be decoded, or if no readable text is found.
        """
        if self.reader is None:
            # Lazy load fallback if not initialized during startup
            self.load_model()

        # 1. Decode image into memory
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB (handles RGBA, grayscale, CMYK, etc.)
            image = image.convert("RGB")
            np_img = np.array(image)
        except Exception as e:
            logger.error("Failed to decode uploaded image: %s", e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to decode image. Please upload a valid image file (JPEG, PNG, WebP)."
            )

        # 2. Perform OCR detection and recognition
        try:
            # detail=0 returns a list of recognized text strings in top-to-bottom reading order
            detected_lines = self.reader.readtext(np_img, detail=0, paragraph=False)
        except Exception as e:
            logger.error("EasyOCR extraction error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"An error occurred while analyzing the image text: {str(e)}"
            )

        # 3. Check for empty or unreadable text
        if not detected_lines:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No readable text found in the uploaded image. "
                    "Please ensure the prescription or report photo is clear, well-lit, and in focus."
                )
            )

        raw_text = "\n".join(line.strip() for line in detected_lines if line.strip())

        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No readable text found in the uploaded image. "
                    "Please ensure the prescription or report photo is clear, well-lit, and in focus."
                )
            )

        # 4. Perform deterministic cleanup for downstream LLM reasoning
        cleaned_text = clean_ocr_text(raw_text)

        return raw_text, cleaned_text


# Singleton instance
ocr_service = EasyOCRService()
