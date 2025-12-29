"""
Streamlit preview demo for certificates (assignment 3).
演示证书预览、PDF转图片、图片处理功能
"""
import os
import tempfile

import streamlit as st
from PIL import Image

from pdf_converter import save_first_page_image
from image_processor import rotate_image, resize_image, image_to_base64
from file_validator import is_allowed_extension


st.set_page_config(page_title="证书预览演示", layout="wide")
st.title("证书预览与图片处理演示")

st.markdown("""
### 功能说明
本页面演示以下功能：
1. **PDF转图片**：将PDF证书的第一页转换为PNG图片
2. **图片预览**：直接展示图片格式的证书
3. **图片处理**：旋转和缩放图片
4. **Base64编码**：将处理后的图片转换为Base64格式（用于API调用）
""")

uploaded = st.file_uploader("上传证书文件 (PDF/JPG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded:
    ext = os.path.splitext(uploaded.name)[1].lower()
    if not is_allowed_extension(uploaded.name):
        st.error("不支持的格式")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, uploaded.name)
        with open(src_path, "wb") as f:
            f.write(uploaded.getvalue())

        st.markdown("### 📄 文件信息")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"文件名：{uploaded.name}")
        with col_info2:
            st.info(f"文件大小：{len(uploaded.getvalue()) / 1024:.1f} KB")

        # PDF转图片或直接加载图片
        if ext == ".pdf":
            st.markdown("### 🔄 PDF转图片")
            image_path = os.path.join(tmpdir, "preview.png")
            try:
                image_path = save_first_page_image(src_path, image_path)
                st.success("✅ PDF转图片成功")
            except Exception as e:
                st.error(f"❌ PDF转图片失败: {e}")
                st.stop()
        else:
            image_path = src_path

        # 加载图片
        try:
            img = Image.open(image_path)
            st.markdown("### 🖼️ 原始图片预览")
            st.image(img, caption="原始图片", use_container_width=True)
        except Exception as e:
            st.error(f"❌ 图片加载失败: {e}")
            st.stop()

        # 图片处理控制
        st.markdown("### ⚙️ 图片处理")
        col_control1, col_control2 = st.columns(2)
        with col_control1:
            rotate_deg = st.slider("旋转角度", -180, 180, 0, step=5)
        with col_control2:
            max_w = st.slider("最大宽度 (像素)", 400, 1600, 1000, step=50)

        # 处理图片
        processed = rotate_image(img, rotate_deg)
        processed = resize_image(processed, max_width=max_w)
        b64 = image_to_base64(processed)

        # 显示处理后的图片
        col_preview1, col_preview2 = st.columns(2)
        with col_preview1:
            st.markdown("#### 处理后预览")
            st.image(processed, caption="处理后图片", use_container_width=True)
        with col_preview2:
            st.markdown("#### Base64编码信息")
            st.caption(f"Base64 长度: {len(b64)} 字符")
            st.text_area(
                "Base64 片段（前500字符）",
                b64[:500] + "..." if len(b64) > 500 else b64,
                height=150,
                disabled=True
            )
            st.download_button(
                "下载完整Base64",
                b64,
                file_name="certificate_base64.txt",
                mime="text/plain"
            )

        # 处理信息
        st.markdown("### 📊 处理信息")
        col_info3, col_info4, col_info5 = st.columns(3)
        with col_info3:
            st.metric("原始尺寸", f"{img.width} × {img.height}")
        with col_info4:
            st.metric("处理后尺寸", f"{processed.width} × {processed.height}")
        with col_info5:
            st.metric("Base64大小", f"{len(b64) / 1024:.1f} KB")


