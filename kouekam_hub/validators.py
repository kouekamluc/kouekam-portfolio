from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError


IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


def validate_uploaded_file(file_obj, allowed_extensions, allowed_content_types=None, label="file"):
    if not file_obj:
        return file_obj

    max_size = int(getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024))
    if file_obj.size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise ValidationError(f"The {label} must be {max_mb}MB or smaller.")

    extension = Path(file_obj.name or "").suffix.lower()
    allowed_extensions = {ext.lower() for ext in allowed_extensions}
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"The {label} must use one of these extensions: {allowed}.")

    content_type = getattr(file_obj, "content_type", "")
    if allowed_content_types and content_type and content_type not in allowed_content_types:
        raise ValidationError(f"The {label} type is not allowed.")

    return file_obj


def validate_image_upload(file_obj, label="image"):
    return validate_uploaded_file(
        file_obj,
        getattr(settings, "ALLOWED_IMAGE_EXTENSIONS", [".jpg", ".jpeg", ".png", ".gif", ".webp"]),
        IMAGE_CONTENT_TYPES,
        label,
    )


def validate_document_upload(file_obj, label="document"):
    return validate_uploaded_file(
        file_obj,
        getattr(settings, "ALLOWED_DOCUMENT_EXTENSIONS", [".pdf", ".doc", ".docx", ".txt", ".md"]),
        DOCUMENT_CONTENT_TYPES,
        label,
    )


def validate_pdf_upload(file_obj, label="PDF"):
    return validate_uploaded_file(file_obj, [".pdf"], {"application/pdf"}, label)
