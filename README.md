# 竞赛证书智能识别与管理系统

基于 Streamlit + SQLModel 的本地可运行示例项目，覆盖以下作业要求：

- 作业一：用户注册/登录、批量导入、RBAC。
- 作业二：文件上传与格式/大小校验、入库记录。
- 作业三：证书预览、PDF 转图片、图片处理与 Base64。

> 仅需本地运行，无需云端部署。示例代码可直接执行，也可按需扩展。

## 快速开始

1. 创建并激活虚拟环境（推荐）：
   ```
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 初始化数据库：
   ```
   python -m database --init
   ```
   生成 `data/app.db` 并创建管理员账号（默认账号/密码：`admin`/`Admin@123`）。
4. 运行主界面（简化版 Streamlit 应用）：
   ```
   streamlit run app.py
   ```
5. 运行预览演示（作业三）：
   ```
   streamlit run preview_demo.py
   ```

## 目录结构

- `app.py`：集成注册、登录、上传、信息核验/提交的示例页面。
- `auth_system.py`：注册、登录、密码加密与校验。
- `user_import.py`：管理员 Excel 批量导入，生成导入报告。
- `database.py`：SQLModel 数据表与 SQLite 会话管理。
- `file_validator.py` / `file_upload.py`：上传校验、保存与入库。
- `pdf_converter.py` / `image_processor.py`：PDF 转图片、图片旋转/缩放/Base64。
- `preview_demo.py`：证书预览与处理演示页面。
- `sample_certificates/`：示例证书（PDF/PNG）。
- `test_files/`：合法/非法上传样例。
- `reports/`：导入/上传/转换测试报告示例。
- `requirements.txt`：依赖清单。
- `init_db.sql`：数据库初始化脚本（与 `database.py` 模型一致）。

## 主要功能点对照

- 注册/登录：学号 13 位、工号 8 位格式校验；bcrypt 加密；RBAC 控制页面展示。
- 批量导入：支持 Excel（.xlsx），唯一性校验，跳过/更新可配置，生成结果统计。
- 文件上传：限制 PDF/JPG/PNG/JPEG，10MB 内；保存至 `uploads/`，记录文件表。
- 预览与处理：PDF 首页转图片，图片旋转/缩放，导出 Base64（方便 OCR 调用）。
- 证书信息：草稿/提交状态、提取方式/置信度字段预留。

## 配置与扩展

- 数据库路径：`database.py` 中的 `DB_PATH`，默认 `data/app.db`。
- 上传目录：`file_upload.py` 的 `UPLOAD_DIR`，默认 `uploads/`。
- 截止时间、默认识别引擎等可写入 `system_config` 表。
- OCR/大模型接入：在 `app.py` 的占位函数 `extract_certificate_fields` 中替换为真实 API 调用（GLM-4V、百度/阿里/腾讯 OCR 或本地 PaddleOCR）。

## 已知环境要求

- Windows 下使用 `pdf2image` 需安装 Poppler，并将 `poppler\bin` 加入 PATH（详见 `pdf_converter.py` 说明）。
- 依赖 `openpyxl` 读写 Excel；`fpdf2` 用于生成示例 PDF。

## 测试与报告

- `import_test_report.md`、`upload_test_report.md`、`conversion_test_results.md` 给出示例测试步骤和结果，可按实际测试更新。
- 样例文件覆盖：合法图片、合法 PDF、非法 TXT/过大文件示例。



