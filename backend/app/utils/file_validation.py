import os
from fastapi import HTTPException, UploadFile, status
from app.config import settings

def validate_image_file(file: UploadFile, file_bytes: bytes) -> None:
    """
    Validates uploaded report/prescription image file size, extension, and content.
    Raises HTTPException with appropriate status code and message if invalid.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing in the uploaded image request."
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported image format '{ext}'. Supported formats are: "
                f"{', '.join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS))}"
            )
        )

    file_size = len(file_bytes)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image file is empty (0 bytes)."
        )

    max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Image file size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed "
                f"limit of {settings.MAX_IMAGE_SIZE_MB} MB."
            )
        )
