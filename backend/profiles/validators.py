from django.core.exceptions import ValidationError

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB

def validate_avatar(file):
    if file is None:
        raise ValidationError("No file provided.")
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationError("Unsupported image type. Use JPEG, PNG, or WEBP.")
    if file.size > MAX_SIZE:
        raise ValidationError("File too large. Max 5MB.")
    return file