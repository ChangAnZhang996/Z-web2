"""
Image processing helpers: rotate, resize, base64.
"""
from __future__ import annotations

import base64
import io
from typing import Tuple

from PIL import Image


def rotate_image(img: Image.Image, degrees: int) -> Image.Image:
    return img.rotate(degrees, expand=True)


def resize_image(img: Image.Image, max_width: int = 1200) -> Image.Image:
    if img.width <= max_width:
        return img
    ratio = max_width / float(img.width)
    new_height = int(img.height * ratio)
    return img.resize((max_width, new_height))


def image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def load_image(path: str) -> Image.Image:
    return Image.open(path)


