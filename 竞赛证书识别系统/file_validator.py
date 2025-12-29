"""
File validation utilities.
"""
from __future__ import annotations

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def is_allowed_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    if not filename:
        return False
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return f".{ext}" in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """Check if file size is within limit."""
    return file_size <= MAX_FILE_SIZE


def validate_file(filename: str, file_size: int) -> tuple[bool, str]:
    """Validate file extension and size."""
    if not is_allowed_extension(filename):
        return False, f"不支持的文件格式。允许的格式：{', '.join(ALLOWED_EXTENSIONS)}"
    if not validate_file_size(file_size):
        return False, f"文件大小超过限制（最大 {MAX_FILE_SIZE / 1024 / 1024}MB）"
    return True, ""


