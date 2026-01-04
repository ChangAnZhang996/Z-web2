"""
Main Streamlit app: registration, login, upload, certificate submission.
"""
from __future__ import annotations

import os
from datetime import datetime
import tempfile
from typing import Dict, Any

import streamlit as st
import pandas as pd
from sqlmodel import select

from auth_system import register_user, authenticate_user, infer_role_by_length, change_password, admin_reset_password
from database import Certificate, User, get_session, init_db, SystemConfig
from file_upload import save_upload
from file_validator import is_allowed_extension
from pdf_converter import save_first_page_image
from image_processor import image_to_base64, resize_image, rotate_image, load_image
from user_import import import_users_from_excel, generate_report
from form_handler import save_draft, submit_certificate, is_before_deadline, get_submission_deadline, load_cert_for_edit, batch_submit
from admin_panel import set_deadline

# 尝试导入GLM-4V相关模块
try:
    from info_extractor import extract_info
    GLM4V_AVAILABLE = True
except ImportError:
    GLM4V_AVAILABLE = False
    # 如果没有GLM-4V模块，使用演示模式
    def extract_info(image_path: str, api_key=None):
        return {
            "student_name": "",
            "student_id": "",
            "department": "",
            "competition_name": "示例竞赛",
            "award_category": "",
            "award_level": "一等奖",
            "competition_type": "",
            "organizer": "示例主办方",
            "award_date": datetime.utcnow().strftime("%Y-%m"),
            "advisor": "",
            "extraction_method": "demo",
            "extraction_confidence": 0.0,
        }


st.set_page_config(page_title="竞赛证书智能识别与管理", layout="wide")

ACCENT = "#7ac28a"  # 淡绿色主题
BG_COLOR = "#f0f9f4"  # 非常淡的绿色背景（偏白）


def inject_css():
    st.markdown(
        f"""
        <style>
        /* 设置整体背景为淡绿色（比已登录状态更淡） */
        .stApp {{
            background-color: {BG_COLOR} !important;
        }}
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            background-color: {BG_COLOR} !important;
        }}
        /* 确保侧边栏背景也是淡绿色 */
        section[data-testid="stSidebar"] {{
            background-color: {BG_COLOR} !important;
        }}
        /* 移除登录注册界面中可能出现的空白文件上传区域 */
        div[data-testid="stFileUploader"]:empty {{
            display: none !important;
        }}
        h1, h2, h3, h4 {{
            color: {ACCENT};
        }}
        .stButton>button {{
            background:{ACCENT};
            color:#0f1b17;
            border-radius:6px;
            border:none;
            font-weight:500;
        }}
        .stDownloadButton>button {{
            background:#e8f6ef;
            color:#0f1b17;
            border:1px solid {ACCENT};
        }}
        .stCheckbox>label {{
            color:#2d5a3d;
        }}
        .welcome-card {{
            background: linear-gradient(135deg, #e8f6ef 0%, #d4edda 100%);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid {ACCENT};
            margin-bottom: 1.5rem;
        }}
        .step-indicator {{
            display: flex;
            justify-content: space-between;
            margin: 2rem 0;
            padding: 0 1rem;
        }}
        .step {{
            flex: 1;
            text-align: center;
            position: relative;
        }}
        .step-number {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {ACCENT};
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        .step-title {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.5rem;
        }}
        .info-box {{
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid {ACCENT};
            margin: 1rem 0;
        }}
        .login-card {{
            background: transparent;
            padding: 2.5rem;
            border-radius: 15px;
            max-width: 500px;
            margin: 2rem auto;
        }}
        .register-card {{
            background: transparent;
            padding: 2.5rem;
            border-radius: 15px;
            max-width: 600px;
            margin: 2rem auto;
        }}
        .admin-header {{
            background: linear-gradient(135deg, #e8f6ef 0%, #d4edda 100%);
            padding: 2rem;
            border-radius: 15px;
            border-left: 5px solid {ACCENT};
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .form-section {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}
        /* 隐藏或修改顶部导航栏颜色 */
        header[data-testid="stHeader"] {{
            background-color: {BG_COLOR} !important;
        }}
        /* 修改顶部工具栏背景 */
        .stDeployButton, div[data-testid="stToolbar"] {{
            background-color: {BG_COLOR} !important;
        }}
        /* 隐藏顶部菜单栏 */
        #MainMenu {{
            visibility: hidden;
        }}
        /* 修改顶部按钮颜色 */
        button[title="Settings"], button[title="Deploy"] {{
            background-color: {BG_COLOR} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("extracted", {})


def logout():
    st.session_state.user = None
    st.session_state.extracted = {}
    st.rerun()


def show_register():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #2d5a3d; margin-bottom: 0.5rem;">📝 用户注册</h1>
            <p style="color: #666; font-size: 1.1rem;">创建您的账号，开始使用证书识别系统</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.container():
        with st.form("register", clear_on_submit=False):
            st.markdown("#### 👤 基本信息")
            col1, col2 = st.columns(2)
            with col1:
                account_id = st.text_input(
                    "学(工)号 *",
                    help="学生13位数字，教师8位数字",
                    placeholder="请输入学号或工号"
                )
                name = st.text_input(
                    "姓名 *",
                    placeholder="请输入真实姓名"
                )
            with col2:
                role = st.selectbox(
                    "角色类型 *",
                    ["student", "teacher"],
                    format_func=lambda x: "👨‍🎓 学生" if x == "student" else "👨‍🏫 教师",
                    help="选择您的身份角色"
                )
                department = st.text_input(
                    "单位/学院 *",
                    placeholder="如：计算机学院"
                )
            
            st.markdown("#### 📧 联系信息")
            email = st.text_input(
                "邮箱地址 *",
                placeholder="example@university.edu.cn",
                help="用于接收系统通知"
            )
            
            st.markdown("#### 🔐 账户安全")
            password = st.text_input(
                "密码 *",
                type="password",
                help="至少8位，包含字母和数字",
                placeholder="请输入密码"
            )
            
            st.markdown(
                """
                <div class="info-box" style="margin-top: 1rem;">
                    <strong>💡 提示：</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>学号需为13位数字（学生）或8位数字（教师）</li>
                        <li>密码需至少8位，包含字母和数字</li>
                        <li>邮箱将用于接收系统通知</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            submitted = st.form_submit_button(
                "✅ 立即注册",
                width='stretch',
                type="primary"
            )
            
            if submitted:
                ok, msg = register_user(account_id, name, password, role, department, email)
                if ok:
                    st.success(f"🎉 {msg}")
                    st.info('请切换到"登录"标签页进行登录')
                else:
                    st.error(f"❌ {msg}")


def show_login():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #2d5a3d; margin-bottom: 0.5rem;">🔐 用户登录</h1>
            <p style="color: #666; font-size: 1.1rem;">使用您的学(工)号和密码登录系统</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.container():
        with st.form("login", clear_on_submit=False):
            account_id = st.text_input(
                "学(工)号",
                placeholder="请输入您的学号或工号",
                help="学生13位数字，教师8位数字"
            )
            password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入您的密码"
            )
            
            st.markdown(
                """
                <div class="info-box" style="margin: 1.5rem 0;">
                    <strong>💡 提示：</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        <li>首次登录请先注册账号</li>
                        <li>忘记密码请联系管理员</li>
                        <li>管理员默认账号：admin / Admin@123</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            submitted = st.form_submit_button(
                "🚀 立即登录",
                width='stretch',
                type="primary"
            )
            
            if submitted:
                ok, user, msg = authenticate_user(account_id, password)
                if ok and user:
                    st.session_state.user = user
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


def extract_certificate_fields(file_path: str) -> Dict[str, Any]:
    """
    使用GLM-4V API提取证书信息
    如果API调用失败，返回空字段供用户手动填写
    """
    file_name = os.path.basename(file_path)
    
    # 确定图片路径（PDF已转换，图片直接使用）
    ext = os.path.splitext(file_path)[1].lower()
    image_path = file_path
    
    # 如果是PDF，尝试使用转换后的预览图片
    if ext == ".pdf":
        # PDF已在上传时转换为PNG预览
        preview_png_path = file_path + ".preview.png"
        if os.path.exists(preview_png_path):
            image_path = preview_png_path
        else:
            # PDF转换失败，无法进行识别
            return {
                "student_name": "",
                "student_id": "",
                "department": "",
                "competition_name": "",
                "award_category": "",
                "award_level": "",
                "competition_type": "",
                "organizer": "",
                "award_date": "",
                "advisor": "",
                "extraction_method": "none",
                "extraction_confidence": 0.0,
                "file_name": file_name,
            }
    
    # 检查是否为图片文件
    if not is_allowed_extension(image_path) or not os.path.exists(image_path):
        # 如果不是图片或文件不存在，返回空字段
        return {
            "student_name": "",
            "student_id": "",
            "department": "",
            "competition_name": "",
            "award_category": "",
            "award_level": "",
            "competition_type": "",
            "organizer": "",
            "award_date": "",
            "advisor": "",
            "extraction_method": "none",
            "extraction_confidence": 0.0,
            "file_name": file_name,
        }
    
    # 尝试使用GLM-4V API提取
    try:
        with st.spinner("正在使用GLM-4V识别证书信息..."):
            extracted = extract_info(image_path)
            extracted["file_name"] = file_name
            if extracted.get("_error"):
                st.warning(f"信息提取失败: {extracted['_error']}。请手动填写信息。")
            else:
                st.success("信息提取成功！请核验并补充缺失字段。")
            return extracted
    except Exception as e:  # noqa: BLE001
        st.warning(f"信息提取失败: {e}。请手动填写信息。")
        return {
            "student_name": "",
            "student_id": "",
            "department": "",
            "competition_name": "",
            "award_category": "",
            "award_level": "",
            "competition_type": "",
            "organizer": "",
            "award_date": "",
            "advisor": "",
            "extraction_method": "failed",
            "extraction_confidence": 0.0,
            "file_name": file_name,
        }


def certificate_form(role: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    # 所有字段都可以修改，不再禁用任何字段
    # 使用卡片容器包装表单
    with st.container():
        st.markdown("#### 📋 基本信息")
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input(
                "学号 (13位数字)",
                value=defaults.get("student_id", ""),
                help="学生学号，13位数字"
            )
            student_name = st.text_input(
                "学生姓名",
                value=defaults.get("student_name", ""),
                help="获奖学生姓名"
            )
            department = st.text_input(
                "所在学院",
                value=defaults.get("department", ""),
                help="学生所属学院或部门"
            )
        with col2:
            competition_name = st.text_input(
                "竞赛项目",
                value=defaults.get("competition_name", ""),
                help="竞赛名称"
            )
            award_category = st.selectbox(
                "获奖类别",
                ["", "国家级", "省级"],
                index=0 if defaults.get("award_category") not in ["国家级", "省级"] else ["", "国家级", "省级"].index(defaults.get("award_category")),
                help="选择获奖类别"
            )
            award_level_options = ["", "特等奖", "一等奖", "二等奖", "三等奖", "金奖", "银奖", "铜奖", "优秀奖"]
            award_level_index = 0
            if defaults.get("award_level") in award_level_options:
                award_level_index = award_level_options.index(defaults.get("award_level"))
            award_level = st.selectbox(
                "获奖等级",
                award_level_options,
                index=award_level_index,
                help="选择获奖等级"
            )
        
        st.markdown("#### 🏆 竞赛详情")
        col3, col4 = st.columns(2)
        with col3:
            competition_type_options = ["", "A类", "B类"]
            competition_type_index = 0
            if defaults.get("competition_type") in competition_type_options:
                competition_type_index = competition_type_options.index(defaults.get("competition_type"))
            competition_type = st.selectbox(
                "竞赛类型",
                competition_type_options,
                index=competition_type_index,
                help="竞赛分类"
            )
            organizer = st.text_input(
                "主办单位",
                value=defaults.get("organizer", ""),
                help="竞赛主办方名称"
            )
        with col4:
            award_date = st.text_input(
                "获奖时间 (YYYY-MM)",
                value=defaults.get("award_date", ""),
                help="格式：2024-09"
            )
            advisor = st.text_input(
                "指导教师（可选）",
                value=defaults.get("advisor", ""),
                help="指导教师的姓名（如无指导教师可留空）"
            )
        
        # 识别信息提示
        extraction_method = defaults.get("extraction_method", "demo")
        extraction_confidence = defaults.get("extraction_confidence", 0.0)
        if extraction_method not in ["demo", "none", "failed"]:
            st.markdown(
                f"""
                <div class="info-box">
                    <strong>🔍 识别信息：</strong> 识别方式: {extraction_method} | 置信度: {extraction_confidence:.0%}
                </div>
                """,
                unsafe_allow_html=True,
            )

    return {
        "student_id": student_id,
        "student_name": student_name,
        "department": department,
        "competition_name": competition_name,
        "award_category": award_category,
        "award_level": award_level,
        "competition_type": competition_type,
        "organizer": organizer,
        "award_date": award_date,
        "advisor": advisor,
        "extraction_method": extraction_method,
        "extraction_confidence": extraction_confidence,
    }


def show_upload_and_form(user: User):
    # 欢迎卡片
    role_name = "学生" if user.role == "student" else "教师"
    st.markdown(
        f"""
        <div class="welcome-card">
            <h3 style="margin-top:0; color:#2d5a3d;">👋 欢迎，{user.name} {role_name}</h3>
            <p style="margin-bottom:0; color:#666;">请上传您的竞赛证书，系统将自动识别并提取信息</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # 步骤指示器
    st.markdown(
        """
        <div class="step-indicator">
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-title">上传证书</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-title">智能识别</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-title">核验信息</div>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <div class="step-title">提交完成</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### 📄 第一步：上传证书文件")
    st.caption("支持格式：PDF、JPG、PNG、JPEG | 文件大小：不超过10MB")
    
    uploaded = st.file_uploader(
        "选择证书文件",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    
    if not uploaded:
        st.info("💡 提示：请先上传证书文件以开始识别流程")
        return

    file_bytes = uploaded.getvalue()
    ok, path, msg = save_upload(user.user_id, uploaded.name, file_bytes)
    if not ok:
        st.error(f"❌ {msg}")
        return
    
    st.success(f"✅ 文件上传成功：{uploaded.name}")

    # 预览区域
    st.markdown("### 🖼️ 第二步：证书预览")
    ext = os.path.splitext(uploaded.name)[1].lower()
    preview_path = path
    pdf_conversion_failed = False
    
    if ext == ".pdf":
        png_path = path + ".preview.png"
        try:
            preview_path = save_first_page_image(path, png_path)
        except Exception as exc:  # noqa: BLE001
            pdf_conversion_failed = True
            error_msg = str(exc)
            st.error(f"❌ PDF 转图片失败: {error_msg}")
            
            # 提供解决方案提示
            if "poppler" in error_msg.lower() or "Unable to get page count" in error_msg or "PyMuPDF" in error_msg or "未安装" in error_msg:
                st.markdown(
                    """
                    <div class="info-box" style="background-color: #fff3cd; border-left-color: #ffc107;">
                        <strong>💡 解决方案（推荐）：</strong>
                        <p>PDF转图片需要安装 <strong>PyMuPDF</strong> 库（无需外部依赖，最简单）。请运行以下命令：</p>
                        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;">
                            <code style="font-size: 1rem;">pip install PyMuPDF</code>
                        </div>
                        <p style="margin-top: 0.5rem;"><strong>备选方案：</strong>如果不想使用 PyMuPDF，也可以安装 Poppler：</p>
                        <ol style="margin: 0.5rem 0; padding-left: 1.5rem;">
                            <li><strong>下载 Poppler：</strong>
                                <ul style="margin: 0.3rem 0; padding-left: 1.5rem;">
                                    <li>访问 <a href="https://github.com/oschwartz10612/poppler-windows/releases" target="_blank">Poppler Windows 下载页面</a></li>
                                    <li>下载最新版本的 zip 文件（例如：Release-XX.XX.X-X.zip）</li>
                                </ul>
                            </li>
                            <li><strong>解压并配置：</strong>
                                <ul style="margin: 0.3rem 0; padding-left: 1.5rem;">
                                    <li>解压到任意目录（例如：<code>C:\\poppler</code>）</li>
                                    <li>将 <code>poppler\\bin</code> 目录添加到系统 PATH 环境变量</li>
                                    <li>或者设置环境变量 <code>POPPLER_PATH=C:\\poppler\\Library\\bin</code></li>
                                </ul>
                            </li>
                            <li><strong>安装 pdf2image：</strong>运行 <code>pip install pdf2image</code></li>
                            <li><strong>重启应用：</strong>配置完成后，重启 Streamlit 应用</li>
                        </ol>
                        <p style="margin-top: 0.5rem;"><strong>临时方案：</strong>如果无法安装上述工具，请直接上传图片格式（JPG/PNG）的证书文件。</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info("💡 提示：如果PDF转换失败，请尝试直接上传图片格式（JPG/PNG）的证书文件。")
    
    # 只有非PDF文件或PDF转换成功时才显示预览
    if not pdf_conversion_failed and is_allowed_extension(preview_path) and os.path.exists(preview_path):
        try:
            img = load_image(preview_path)
            img = rotate_image(img, 0)
            # 缩小预览图片，使其能在一个屏幕内完整显示（缩小到350px）
            img = resize_image(img, 500)
            
            # 使用卡片容器展示预览
            with st.container():
                st.image(img, caption="证书预览", width=500)
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.caption(f"📏 文件大小: {len(file_bytes) / 1024:.1f} KB")
                with col_info2:
                    st.caption(f"🔢 Base64 长度: {len(image_to_base64(img))} 字符")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"⚠️ 预览失败: {exc}")
    elif ext == ".pdf" and pdf_conversion_failed:
        # PDF转换失败时，提示用户可以继续填写表单
        st.info("💡 虽然PDF预览失败，但您仍可以继续填写证书信息并提交。")

    # 信息提取（如果PDF转换失败，跳过图片识别，使用空字段）
    st.markdown("### 🤖 第三步：智能识别信息")
    if ext == ".pdf" and pdf_conversion_failed:
        st.warning("⚠️ PDF转换失败，无法进行智能识别。请手动填写证书信息。")
        extracted = {
            "student_name": "",
            "student_id": "",
            "department": "",
            "competition_name": "",
            "award_category": "",
            "award_level": "",
            "competition_type": "",
            "organizer": "",
            "award_date": "",
            "advisor": "",
            "extraction_method": "manual",
            "extraction_confidence": 0.0,
            "file_name": os.path.basename(path),
        }
    else:
        extracted = extract_certificate_fields(path)
    st.session_state.extracted = extracted

    defaults = {
        "student_id": user.account_id if user.role == "student" else "",
        "student_name": user.name if user.role == "student" else "",
        "advisor": user.name if user.role == "teacher" else "",
        **extracted,
    }
    
    # 表单区域
    st.markdown("### ✏️ 第四步：核验并完善信息")
    st.markdown(
        f"""
        <div class="info-box">
            <strong>💡 提示：</strong>
            {"您的学号和姓名已自动填充，请核验其他信息。指导教师为可选字段。" if user.role == "student" 
              else "请填写被指导学生的学号和姓名。您的姓名已自动填充为指导教师，如无指导教师可留空。"}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    payload = certificate_form(user.role, defaults)

    # 截止时间提示
    deadline = get_submission_deadline()
    if deadline:
        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline)
            now = datetime.utcnow()
            if now > deadline_dt:
                st.error(f"❌ 提交截止时间已过：{deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                days_left = (deadline_dt - now).days
                st.info(f"⏰ 提交截止时间：{deadline_dt.strftime('%Y-%m-%d %H:%M:%S')} （还剩 {days_left} 天）")
        except Exception:
            pass

    # 提交按钮区域
    st.markdown("---")
    st.markdown("### 📤 提交信息")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 保存草稿", width='stretch', type="secondary"):
            if not is_before_deadline():
                st.error("❌ 提交截止时间已过，无法保存草稿")
            else:
                payload["submitter_role"] = user.role
                cert_id = save_draft(user.user_id, payload, path)
                st.success("✅ 草稿保存成功")
                st.rerun()
    with col2:
        if st.button("✅ 提交", width='stretch', type="primary"):
            if not is_before_deadline():
                st.error("❌ 提交截止时间已过，无法提交")
                return
            # Basic required checks
            if len(payload["student_id"]) != 13 or not payload["student_id"].isdigit():
                st.error("❌ 学号需为13位数字")
                return
            if not payload["student_name"]:
                st.error("❌ 学生姓名必填")
                return
            # 指导教师为可选字段，不再强制要求
            payload["submitter_role"] = user.role
            cert_id = save_draft(user.user_id, payload, path)
            if submit_certificate(cert_id, user.user_id):
                st.success("✅ 提交成功")
                st.balloons()  # 提交成功动画效果
                st.rerun()
            else:
                st.error("❌ 提交失败")


def show_edit_draft(user: User, draft_data: Dict[str, Any]):
    """编辑草稿界面"""
    st.markdown("### ✏️ 编辑草稿")
    
    # 显示草稿信息提示
    st.info(f"📝 正在编辑草稿：{draft_data.get('competition_name', '未命名')} - {draft_data.get('created_at', '')}")
    
    # 如果有文件路径，尝试显示预览
    file_path = draft_data.get("file_path", "")
    if file_path and os.path.exists(file_path):
        st.markdown("### 🖼️ 证书预览")
        ext = os.path.splitext(file_path)[1].lower()
        preview_path = file_path
        if ext == ".pdf":
            png_path = file_path + ".preview.png"
            if os.path.exists(png_path):
                preview_path = png_path
        
        pdf_preview_available = False
        if ext == ".pdf":
            png_path = file_path + ".preview.png"
            if os.path.exists(png_path):
                preview_path = png_path
                pdf_preview_available = True
            else:
                # 尝试转换PDF
                try:
                    preview_path = save_first_page_image(file_path, png_path)
                    pdf_preview_available = True
                except Exception as exc:  # noqa: BLE001
                    error_msg = str(exc)
                    st.warning(f"⚠️ PDF预览不可用: {error_msg}")
                    if "poppler" in error_msg.lower() or "Unable to get page count" in error_msg:
                        st.info("💡 提示：PDF预览需要安装Poppler工具，但不影响编辑功能。您可以继续编辑证书信息。")
                    else:
                        st.info("💡 提示：PDF预览失败，但不影响编辑功能。")
        
        if pdf_preview_available or ext != ".pdf":
            if is_allowed_extension(preview_path) and os.path.exists(preview_path):
                try:
                    img = load_image(preview_path)
                    img = rotate_image(img, 0)
                    img = resize_image(img, 500)
                    st.image(img, caption="证书预览", width=500)
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"⚠️ 预览失败: {exc}")
            else:
                st.info("💡 证书文件预览不可用")
        else:
            st.info("💡 PDF预览不可用，但不影响编辑功能。")
    
    # 准备表单默认值
    defaults = {
        "student_id": draft_data.get("student_id", ""),
        "student_name": draft_data.get("student_name", ""),
        "department": draft_data.get("department", ""),
        "competition_name": draft_data.get("competition_name", ""),
        "award_category": draft_data.get("award_category", ""),
        "award_level": draft_data.get("award_level", ""),
        "competition_type": draft_data.get("competition_type", ""),
        "organizer": draft_data.get("organizer", ""),
        "award_date": draft_data.get("award_date", ""),
        "advisor": draft_data.get("advisor", ""),
        "extraction_method": draft_data.get("extraction_method", ""),
        "extraction_confidence": draft_data.get("extraction_confidence", 0.0),
    }
    
    # 表单区域
    st.markdown("### ✏️ 修改信息")
    payload = certificate_form(user.role, defaults)
    
    # 截止时间提示
    deadline = get_submission_deadline()
    if deadline:
        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline)
            now = datetime.utcnow()
            if now > deadline_dt:
                st.error(f"❌ 提交截止时间已过：{deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                days_left = (deadline_dt - now).days
                st.info(f"⏰ 提交截止时间：{deadline_dt.strftime('%Y-%m-%d %H:%M:%S')} （还剩 {days_left} 天）")
        except Exception:
            pass
    
    # 操作按钮区域
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("💾 保存修改", width='stretch', type="primary"):
            if not is_before_deadline():
                st.error("❌ 提交截止时间已过，无法保存草稿")
            else:
                payload["submitter_role"] = user.role
                cert_id = save_draft(user.user_id, payload, file_path)
                st.success("✅ 草稿保存成功")
                # 清除编辑状态，返回草稿列表
                if "edit_draft_id" in st.session_state:
                    del st.session_state.edit_draft_id
                st.rerun()
    with col2:
        if st.button("✅ 提交", width='stretch', type="primary"):
            if not is_before_deadline():
                st.error("❌ 提交截止时间已过，无法提交")
            else:
                # Basic required checks
                if len(payload["student_id"]) != 13 or not payload["student_id"].isdigit():
                    st.error("❌ 学号需为13位数字")
                elif not payload["student_name"]:
                    st.error("❌ 学生姓名必填")
                # 指导教师为可选字段，不再强制要求
                else:
                    draft_id = draft_data.get("cert_id")
                    if draft_id:
                        # 先更新草稿数据
                        payload["submitter_role"] = user.role
                        save_draft(user.user_id, payload, file_path)
                        # 然后提交
                        if submit_certificate(draft_id, user.user_id):
                            st.success("✅ 提交成功")
                            st.balloons()
                            if "edit_draft_id" in st.session_state:
                                del st.session_state.edit_draft_id
                            st.rerun()
                        else:
                            st.error("❌ 提交失败")
                    else:
                        st.error("❌ 草稿ID不存在")
    with col3:
        if st.button("❌ 取消编辑", width='stretch', type="secondary"):
            if "edit_draft_id" in st.session_state:
                del st.session_state.edit_draft_id
            st.rerun()
    with col4:
        st.write("")  # 占位


def show_change_password(user: User):
    """修改密码界面"""
    st.markdown("### 🔐 修改密码")
    with st.form("change_password"):
        old_password = st.text_input("原密码", type="password")
        new_password = st.text_input("新密码", type="password", help="至少8位，包含字母和数字")
        confirm_password = st.text_input("确认新密码", type="password")
        submitted = st.form_submit_button("修改密码", width='stretch', type="primary")
        
        if submitted:
            if new_password != confirm_password:
                st.error("❌ 两次输入的密码不一致")
            else:
                ok, msg = change_password(user.user_id, old_password, new_password)
                if ok:
                    st.success(f"✅ {msg}")
                    st.info("请重新登录以使用新密码")
                else:
                    st.error(f"❌ {msg}")


def show_my_drafts(user: User):
    """查看我的草稿列表"""
    st.markdown("### 📝 我的草稿")
    
    with get_session() as session:
        drafts = session.exec(
            select(Certificate).where(
                (Certificate.submitter_id == user.user_id) & (Certificate.status == "draft")
            ).order_by(Certificate.created_at.desc())
        ).all()
    
    if not drafts:
        st.info("暂无草稿")
        return
    
    st.write(f"共 {len(drafts)} 条草稿")
    
    for draft in drafts:
        with st.expander(f"📄 {draft.competition_name or '未命名'} - {draft.created_at.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**学生姓名：** {draft.student_name}")
                st.write(f"**学号：** {draft.student_id}")
                st.write(f"**竞赛项目：** {draft.competition_name}")
                st.write(f"**获奖等级：** {draft.award_level}")
            with col2:
                st.write(f"**获奖类别：** {draft.award_category}")
                st.write(f"**竞赛类型：** {draft.competition_type}")
                st.write(f"**获奖时间：** {draft.award_date}")
                st.write(f"**指导教师：** {draft.advisor}")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("编辑", key=f"edit_{draft.cert_id}"):
                    st.session_state.edit_draft_id = draft.cert_id
                    st.rerun()
            with col_btn2:
                if st.button("提交", key=f"submit_{draft.cert_id}"):
                    if submit_certificate(draft.cert_id, user.user_id):
                        st.success("✅ 提交成功")
                        st.rerun()
                    else:
                        st.error("❌ 提交失败，可能已超过截止时间")
            with col_btn3:
                if st.button("删除", key=f"delete_{draft.cert_id}"):
                    with get_session() as session:
                        cert = session.get(Certificate, draft.cert_id)
                        if cert:
                            session.delete(cert)
                            session.commit()
                            st.success("✅ 删除成功")
                            st.rerun()


def show_admin_tools(user: User):
    # 管理员欢迎卡片
    st.markdown(
        f"""
        <div class="admin-header">
            <h2 style="margin-top:0; color:#2d5a3d;">👨‍💼 管理员控制台</h2>
            <p style="margin-bottom:0; color:#666; font-size:1.1rem;">欢迎，{user.name}！您可以在这里管理用户、查看数据和批量导入</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with get_session() as session:
        users = session.exec(select(User)).all()
        certs = session.exec(select(Certificate)).all()

    # 数据概览卡片
    st.markdown("### 📊 数据概览")
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem; color: {ACCENT}; font-weight: bold;">{len(users)}</div>
                <div style="color: #666; margin-top: 0.5rem;">👥 用户总数</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        submitted_count = sum(c.status == "submitted" for c in certs)
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem; color: {ACCENT}; font-weight: bold;">{submitted_count}</div>
                <div style="color: #666; margin-top: 0.5rem;">✅ 已提交</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_c:
        draft_count = sum(c.status == "draft" for c in certs)
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem; color: #ffc107; font-weight: bold;">{draft_count}</div>
                <div style="color: #666; margin-top: 0.5rem;">📝 草稿</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_d:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size: 2.5rem; color: {ACCENT}; font-weight: bold;">{len(certs)}</div>
                <div style="color: #666; margin-top: 0.5rem;">📋 总记录</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📥 批量导入用户")
    
    with st.container(border=True):
        st.markdown(
            """
            <div class="form-section">
                <h4 style="margin-top:0; color:#2d5a3d;">📋 Excel批量导入</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            update_existing = st.checkbox(
                "✅ 已存在账号时更新信息（不勾选则跳过）",
                value=False,
                help="勾选后，如果账号已存在，将更新该账号的信息"
            )
            uploaded_excel = st.file_uploader(
                "上传 Excel 文件 (.xlsx)",
                type=["xlsx"],
                key="admin_excel_uploader",
                help="请上传符合格式要求的Excel文件"
            )
            
            if uploaded_excel and st.button("🚀 开始导入", type="primary", width='stretch'):
                with st.spinner("正在导入用户数据..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        tmp.write(uploaded_excel.getvalue())
                        tmp_path = tmp.name
                    try:
                        stats = import_users_from_excel(tmp_path, update_existing=update_existing)
                        report = generate_report(stats)
                        st.success("✅ 导入完成！")
                        st.markdown(
                            f"""
                            <div class="info-box">
                                {report}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"❌ 导入失败: {exc}")
        
        with col2:
            st.markdown("#### 📄 导入模板")
            template_path = "sample_users.xlsx"
            if os.path.exists(template_path):
                with open(template_path, "rb") as f:
                    st.download_button(
                        "📥 下载模板",
                        f.read(),
                        file_name="user_import_template.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch',
                    )
            else:
                st.info("💡 模板文件不存在，请先运行 `python generate_samples.py` 生成")
            
            st.markdown(
                """
                <div class="info-box" style="margin-top: 1rem;">
                    <strong>📝 Excel格式要求：</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.9rem;">
                        <li><strong>必填列：</strong>学(工)号、姓名、角色、单位、邮箱</li>
                        <li><strong>可选列：</strong>password（未填则自动生成）</li>
                        <li><strong>角色值：</strong>student / teacher / admin</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 截止时间管理
    st.markdown("### ⏰ 截止时间管理")
    with st.container(border=True):
        deadline = get_submission_deadline()
        if deadline:
            try:
                from datetime import datetime
                deadline_dt = datetime.fromisoformat(deadline)
                st.info(f"当前截止时间：{deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception:
                st.info(f"当前截止时间：{deadline}")
        else:
            st.info("未设置截止时间")
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            new_deadline = st.text_input(
                "设置截止时间 (ISO格式)",
                value=deadline or "",
                placeholder="2025-01-31T23:59:59",
                help="格式：YYYY-MM-DDTHH:MM:SS"
            )
        with col_dl2:
            st.write("")  # 占位
            if st.button("设置截止时间", width='stretch'):
                if new_deadline:
                    try:
                        from datetime import datetime
                        datetime.fromisoformat(new_deadline)  # 验证格式
                        if set_deadline(new_deadline, user.user_id):
                            st.success("✅ 截止时间设置成功")
                            st.rerun()
                        else:
                            st.error("❌ 设置失败")
                    except Exception as e:
                        st.error(f"❌ 时间格式错误：{e}")
                else:
                    st.error("❌ 请输入截止时间")
    
    # 数据导出
    st.markdown("### 📤 数据导出")
    with st.container(border=True):
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("导出CSV", width='stretch'):
                from data_export import export_to_csv
                from datetime import datetime
                filename = f"certificates_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                try:
                    export_to_csv(filename)
                    with open(filename, "rb") as f:
                        st.download_button(
                            "下载CSV文件",
                            f.read(),
                            file_name=filename,
                            mime="text/csv"
                        )
                    st.success("✅ CSV导出成功")
                except Exception as e:
                    st.error(f"❌ 导出失败：{e}")
        with col_exp2:
            if st.button("导出Excel", width='stretch'):
                from data_export import export_to_excel
                from datetime import datetime
                filename = f"certificates_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                try:
                    export_to_excel(filename)
                    with open(filename, "rb") as f:
                        st.download_button(
                            "下载Excel文件",
                            f.read(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success("✅ Excel导出成功")
                except Exception as e:
                    st.error(f"❌ 导出失败：{e}")

    st.markdown("### 📊 数据查看")
    
    tabs = st.tabs(["👥 用户列表", "📋 提交记录", "📈 统计信息"])
    
    with tabs[0]:
        st.markdown("#### 所有注册用户")
        
        # 搜索和筛选功能
        col_search1, col_search2, col_search3 = st.columns([2, 2, 1])
        with col_search1:
            search_keyword = st.text_input(
                "🔍 搜索用户",
                placeholder="输入学(工)号、姓名或邮箱",
                key="user_search"
            )
        with col_search2:
            role_filter = st.selectbox(
                "筛选角色",
                ["全部", "student", "teacher", "admin"],
                format_func=lambda x: {"全部": "全部", "student": "👨‍🎓 学生", "teacher": "👨‍🏫 教师", "admin": "👨‍💼 管理员"}.get(x, x),
                key="role_filter"
            )
        with col_search3:
            st.write("")  # 占位
        
        # 筛选用户
        filtered_users = users
        if search_keyword:
            keyword_lower = search_keyword.lower()
            filtered_users = [
                u for u in filtered_users
                if keyword_lower in u.account_id.lower()
                or keyword_lower in u.name.lower()
                or keyword_lower in u.email.lower()
            ]
        if role_filter != "全部":
            filtered_users = [u for u in filtered_users if u.role == role_filter]
        
        if filtered_users:
            try:
                # 显示用户列表，每行带重置密码按钮
                st.markdown("---")
                for idx, u in enumerate(filtered_users):
                    with st.container(border=True):
                        col_user1, col_user2, col_user3 = st.columns([3, 2, 1])
                        with col_user1:
                            role_icon = {"student": "👨‍🎓", "teacher": "👨‍🏫", "admin": "👨‍💼"}.get(u.role, "👤")
                            st.markdown(
                                f"""
                                <div style="padding: 0.5rem 0;">
                                    <strong>{role_icon} {u.name}</strong><br>
                                    <span style="color: #666; font-size: 0.9rem;">
                                        学(工)号: {u.account_id} | 邮箱: {u.email}
                                    </span><br>
                                    <span style="color: #666; font-size: 0.85rem;">
                                        单位: {u.department or '未填写'} | 
                                        状态: {'✅ 启用' if u.is_active else '❌ 禁用'}
                                    </span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        with col_user2:
                            st.write("")  # 占位
                        with col_user3:
                            # 重置密码按钮
                            reset_key = f"reset_pwd_{u.user_id}_{idx}"
                            if st.button("🔑 重置密码", key=reset_key, use_container_width=True, type="secondary"):
                                if u.role == "admin":
                                    st.warning("⚠️ 不能重置管理员密码")
                                else:
                                    ok, msg = admin_reset_password(user.user_id, u.account_id)
                                    if ok:
                                        st.success(f"✅ {msg}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                
                st.caption(f"共显示 {len(filtered_users)} / {len(users)} 位用户")
            except Exception as exc:  # noqa: BLE001
                st.error(f"❌ 显示用户列表失败: {exc}")
                # 降级显示：使用DataFrame
                users_df = pd.DataFrame([u.model_dump() for u in filtered_users])
                for col in users_df.select_dtypes(include=["object"]).columns:
                    users_df[col] = users_df[col].astype(str)
                st.dataframe(users_df, width='stretch', hide_index=True)
        else:
            st.info("暂无符合条件的用户数据")
    
    with tabs[1]:
        st.markdown("#### 所有证书提交记录")
        if certs:
            try:
                certs_df = pd.DataFrame([c.model_dump() for c in certs])
                for col in certs_df.select_dtypes(include=["object"]).columns:
                    certs_df[col] = certs_df[col].astype(str)
                st.dataframe(
                    certs_df,
                    width='stretch',
                    hide_index=True,
                )
                st.caption(f"共 {len(certs)} 条记录")
            except Exception as exc:  # noqa: BLE001
                st.error(f"❌ 显示提交记录失败: {exc}")
                st.write(certs)
        else:
            st.info("暂无提交记录")
    
    with tabs[2]:
        st.markdown("#### 📈 数据统计")
        
        # 用户统计
        st.markdown("##### 👥 用户统计")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            student_count = sum(1 for u in users if u.role == "student")
            st.metric("学生用户", student_count)
        with col_stat2:
            teacher_count = sum(1 for u in users if u.role == "teacher")
            st.metric("教师用户", teacher_count)
        with col_stat3:
            admin_count = sum(1 for u in users if u.role == "admin")
            st.metric("管理员", admin_count)
        
        # 证书统计
        st.markdown("##### 🏆 证书统计")
        if certs:
            col_stat4, col_stat5 = st.columns(2)
            with col_stat4:
                submitted_certs = [c for c in certs if c.status == "submitted"]
                st.metric("已提交证书", len(submitted_certs))
            with col_stat5:
                draft_certs = [c for c in certs if c.status == "draft"]
                st.metric("草稿证书", len(draft_certs))
            
            # 获奖等级统计
            if submitted_certs:
                st.markdown("##### 🎖️ 获奖等级分布")
                award_levels = {}
                for cert in submitted_certs:
                    level = cert.award_level or "未填写"
                    award_levels[level] = award_levels.get(level, 0) + 1
                
                if award_levels:
                    for level, count in sorted(award_levels.items(), key=lambda x: x[1], reverse=True):
                        st.progress(count / len(submitted_certs), text=f"{level}: {count} 项")
        else:
            st.info("暂无统计数据")


def main():
    # 确保数据库表已创建
    from database import SQLModel, engine
    SQLModel.metadata.create_all(engine)
    # 确保管理员账户已创建
    init_db()  # 添加这一行
    
    inject_css()
    init_state()
    user = st.session_state.user

    if not user:
        # 添加页面标题和说明
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="color: #2d5a3d; margin-bottom: 1rem;">🏆 竞赛证书智能识别与管理系统</h1>
                <p style="color: #666; font-size: 1.2rem; margin-bottom: 2rem;">
                    基于AI视觉识别的证书信息自动提取与管理平台
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        tab_login, tab_register = st.tabs(["🔐 登录", "📝 注册"])
        with tab_login:
            show_login()
        with tab_register:
            show_register()
        return

    st.sidebar.success(f"已登录: {user.name} ({user.role})")
    
    # 侧边栏菜单
    if user.role == "admin":
        menu_option = st.sidebar.selectbox(
            "功能菜单",
            ["管理控制台", "修改密码"],
            key="admin_menu"
        )
    else:
        # 如果有待编辑的草稿，自动切换到"上传证书"页面
        if "edit_draft_id" in st.session_state and st.session_state.edit_draft_id:
            # 强制菜单选项为"上传证书"以显示编辑界面
            menu_option = "上传证书"
        else:
            menu_option = st.sidebar.selectbox(
                "功能菜单",
                ["上传证书", "我的草稿", "修改密码"],
                key="user_menu"
            )
    
    if st.sidebar.button("退出登录"):
        logout()
    
    # 显示截止时间（所有用户）
    deadline = get_submission_deadline()
    if deadline:
        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline)
            now = datetime.utcnow()
            if now > deadline_dt:
                st.sidebar.error(f"⏰ 截止时间已过")
            else:
                days_left = (deadline_dt - now).days
                st.sidebar.info(f"⏰ 还剩 {days_left} 天")
        except Exception:
            pass

    # 根据菜单选项显示不同界面
    if user.role == "admin":
        if menu_option == "管理控制台":
            show_admin_tools(user)
        elif menu_option == "修改密码":
            show_change_password(user)
    else:
        if menu_option == "上传证书":
            # 检查是否有待编辑的草稿
            if "edit_draft_id" in st.session_state and st.session_state.edit_draft_id:
                draft_data = load_cert_for_edit(st.session_state.edit_draft_id, user.user_id)
                if draft_data:
                    show_edit_draft(user, draft_data)
                else:
                    del st.session_state.edit_draft_id
                    show_upload_and_form(user)
            else:
                show_upload_and_form(user)
        elif menu_option == "我的草稿":
            show_my_drafts(user)
        elif menu_option == "修改密码":
            show_change_password(user)


if __name__ == "__main__":
    main()

