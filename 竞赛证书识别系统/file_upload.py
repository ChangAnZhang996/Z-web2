"""
File upload handling.
"""
from __future__ import annotations

import os
import time
import random
from datetime import datetime

from database import File, get_session
from file_validator import validate_file


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(user_id: int, filename: str, file_bytes: bytes) -> tuple[bool, str, str]:
    """Save uploaded file and record in database."""
    ok, msg = validate_file(filename, len(file_bytes))
    if not ok:
        return False, "", msg

    # Generate unique filename with microsecond precision and random suffix to avoid conflicts
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds
    random_suffix = random.randint(1000, 9999)  # 4-digit random number
    name_part = os.path.splitext(filename)[0][:20]  # Limit name length
    ext = os.path.splitext(filename)[1]
    unique_name = f"{user_id}_{timestamp}_{random_suffix}_{name_part}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Ensure file doesn't exist (very unlikely but check anyway)
    counter = 1
    while os.path.exists(file_path):
        unique_name = f"{user_id}_{timestamp}_{random_suffix}_{counter}_{name_part}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        counter += 1

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        return False, "", f"文件保存失败: {e}"

    # Record in database
    try:
        file_type = "pdf" if ext.lower() == ".pdf" else "image"
        with get_session() as session:
            file_record = File(
                user_id=user_id,
                file_name=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=len(file_bytes),
            )
            session.add(file_record)
            session.commit()
        return True, file_path, "文件上传成功"
    except Exception as e:
        # File saved but DB record failed - still return success
        return True, file_path, f"文件已保存，但数据库记录失败: {e}"


