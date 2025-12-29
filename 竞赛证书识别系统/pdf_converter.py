"""
PDF to image utilities.
支持两种方式：PyMuPDF (推荐，无需外部依赖) 和 pdf2image (需要 Poppler)
"""
from __future__ import annotations

import io
import os
from typing import List, Optional

from PIL import Image

# 优先尝试使用 PyMuPDF (fitz)，无需外部依赖
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

# 备选方案：pdf2image (需要 Poppler)
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None

# On Windows, install Poppler and set POPPLER_PATH or pass poppler_path explicitly.
POPPLER_PATH = os.environ.get("POPPLER_PATH")


def pdf_to_images_pymupdf(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
    """使用 PyMuPDF 将 PDF 转换为图片列表（推荐方法，无需外部依赖）"""
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF 未安装，请运行: pip install PyMuPDF")
    
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 计算缩放因子以匹配 DPI
        zoom = dpi / 72.0  # 72 是默认 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为 PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    
    doc.close()
    return images


def pdf_to_images_pdf2image(pdf_path: str, poppler_path: Optional[str] = POPPLER_PATH, dpi: int = 200) -> List[Image.Image]:
    """使用 pdf2image 将 PDF 转换为图片列表（需要 Poppler）"""
    if not PDF2IMAGE_AVAILABLE:
        raise ImportError("pdf2image 未安装，请运行: pip install pdf2image")
    return convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)


def pdf_to_images(pdf_path: str, poppler_path: Optional[str] = POPPLER_PATH, dpi: int = 200) -> List[Image.Image]:
    """
    将 PDF 转换为图片列表
    优先使用 PyMuPDF（无需外部依赖），失败则尝试 pdf2image
    """
    # 优先尝试 PyMuPDF
    if PYMUPDF_AVAILABLE:
        try:
            return pdf_to_images_pymupdf(pdf_path, dpi=dpi)
        except Exception as e:
            # PyMuPDF 失败，尝试 pdf2image
            if PDF2IMAGE_AVAILABLE:
                try:
                    return pdf_to_images_pdf2image(pdf_path, poppler_path=poppler_path, dpi=dpi)
                except Exception:
                    raise RuntimeError(f"PDF转换失败。PyMuPDF错误: {e}，pdf2image也失败")
            else:
                raise RuntimeError(f"PyMuPDF转换失败: {e}，且pdf2image未安装")
    
    # 如果没有 PyMuPDF，使用 pdf2image
    if PDF2IMAGE_AVAILABLE:
        return pdf_to_images_pdf2image(pdf_path, poppler_path=poppler_path, dpi=dpi)
    
    # 两者都不可用
    raise ImportError(
        "PDF转换库未安装。请安装其中一个：\n"
        "  - PyMuPDF (推荐): pip install PyMuPDF\n"
        "  - pdf2image: pip install pdf2image (还需要安装 Poppler)"
    )


def save_first_page_image(pdf_path: str, output_path: str, poppler_path: Optional[str] = POPPLER_PATH) -> str:
    """
    保存 PDF 第一页为图片
    优先使用 PyMuPDF（无需外部依赖）
    """
    import io
    
    # 优先尝试 PyMuPDF
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                doc.close()
                raise ValueError("PDF 文件为空")
            
            page = doc[0]
            # 使用 200 DPI 的缩放因子
            zoom = 200 / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # 保存为 PNG
            pix.save(output_path)
            doc.close()
            return output_path
        except Exception as e:
            # PyMuPDF 失败，尝试 pdf2image
            if PDF2IMAGE_AVAILABLE:
                try:
                    images = pdf_to_images_pdf2image(pdf_path, poppler_path=poppler_path)
                    if not images:
                        raise ValueError("无法从 PDF 转出图片")
                    images[0].save(output_path, format="PNG")
                    return output_path
                except Exception:
                    raise RuntimeError(f"PDF转换失败。PyMuPDF错误: {e}，pdf2image也失败")
            else:
                raise RuntimeError(f"PyMuPDF转换失败: {e}，且pdf2image未安装")
    
    # 如果没有 PyMuPDF，使用 pdf2image
    if PDF2IMAGE_AVAILABLE:
        images = pdf_to_images_pdf2image(pdf_path, poppler_path=poppler_path)
        if not images:
            raise ValueError("无法从 PDF 转出图片")
        images[0].save(output_path, format="PNG")
        return output_path
    
    # 两者都不可用
    raise ImportError(
        "PDF转换库未安装。请安装其中一个：\n"
        "  - PyMuPDF (推荐): pip install PyMuPDF\n"
        "  - pdf2image: pip install pdf2image (还需要安装 Poppler)"
    )


