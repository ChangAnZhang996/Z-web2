# 竞赛证书智能识别与管理系统

基于 Streamlit + SQLModel + GLM-4V 的智能证书识别与管理系统，完整实现了五个作业任务的所有功能要求。

## 📋 作业任务说明

本项目包含五个作业任务，每个任务都有对应的代码文件和测试材料：

### 作业一：用户注册与登录 ✅

**功能要求：**
1. ✅ 实现三种角色的用户注册（学生13位学号、教师8位工号、管理员）
2. ✅ 学(工)号格式验证和唯一性检查
3. ✅ 使用 `bcrypt` 加密存储密码
4. ✅ 用户登录功能（支持学(工)号登录）
5. ✅ 管理员批量导入用户（Excel文件）
6. ✅ 导入验证逻辑（重复记录检查、自动创建账号）
7. ✅ 生成导入报告（成功、失败、重复记录）
8. ✅ 实现基于角色的权限控制（RBAC）

**对应文件：**
- `auth_system.py` - 用户认证系统代码（注册、登录、密码管理）
- `user_import.py` - 用户批量导入代码
- `database.py` - 数据库操作代码（用户表、会话管理）
- `init_db.sql` - 数据库初始化脚本
- `sample_users.xlsx` - 用户导入模板和测试数据
- `requirements.txt` - 项目依赖清单
- `import_test_report.md` - 批量导入测试报告（如存在）

**功能验证：**
- ✅ 学生注册（13位学号验证）
- ✅ 教师注册（8位工号验证）
- ✅ 密码bcrypt加密存储
- ✅ 用户登录验证
- ✅ Excel批量导入用户
- ✅ 导入报告生成
- ✅ RBAC权限控制（学生/教师/管理员不同界面）

---

### 作业二：文件上传与格式验证 ✅

**功能要求：**
1. ✅ 实现文件上传组件，支持PDF和图片格式
2. ✅ 验证文件格式（仅允许PDF、JPG、PNG、JPEG）
3. ✅ 限制文件大小（不超过10MB）
4. ✅ 将上传文件保存到指定目录
5. ✅ 在数据库中记录文件信息（文件名、路径、类型、大小、上传时间）
6. ✅ 实现文件上传失败的错误提示

**对应文件：**
- `file_upload.py` - 文件上传处理代码
- `file_validator.py` - 文件验证代码（格式、大小）
- `test_files/` - 测试用的样本文件（包含合法和非法文件）
- `upload_test_report.md` - 文件上传测试报告（如存在）

**功能验证：**
- ✅ PDF文件上传和验证
- ✅ 图片文件上传和验证（JPG、PNG、JPEG）
- ✅ 文件大小限制（10MB）
- ✅ 文件保存到 `uploads/` 目录
- ✅ 数据库记录文件信息
- ✅ 错误提示（格式错误、大小超限等）

---

### 作业三：证书预览、PDF转图片、图片处理与Base64 ✅

**功能要求：**
1. ✅ 实现PDF转图片功能（提取PDF第一页）
2. ✅ 实现图片文件直接显示功能
3. ✅ 在Streamlit中预览证书图片
4. ✅ 实现图片转Base64编码格式（用于API调用）
5. ✅ 实现图片旋转和尺寸调整功能

**对应文件：**
- `image_processor.py` - 图片处理代码（旋转、缩放、Base64编码）
- `pdf_converter.py` - PDF转图片代码（支持PyMuPDF和pdf2image）
- `preview_demo.py` - 证书预览演示页面
- `sample_certificates/` - 示例证书文件
- `conversion_test_results.md` - 转换测试结果报告（如存在）

**功能验证：**
- ✅ PDF转PNG图片（提取第一页）
- ✅ 图片文件直接显示
- ✅ Streamlit预览界面
- ✅ 图片转Base64编码
- ✅ 图片旋转功能
- ✅ 图片尺寸调整功能

---

### 作业四：GLM-4V API集成与信息提取 ✅

**功能要求：**
1. ✅ 注册并获取GLM-4V API密钥
2. ✅ 实现API调用函数（发送证书图片和提取提示词）
3. ✅ 解析API返回的JSON结果
4. ✅ 提取10个字段信息：
   - ✅ 学生所在学院
   - ✅ 竞赛项目
   - ✅ 学号
   - ✅ 学生姓名
   - ✅ 获奖类别
   - ✅ 获奖等级
   - ✅ 竞赛类型
   - ✅ 主办单位
   - ✅ 获奖时间
   - ✅ 指导教师
5. ✅ 处理API调用失败和字段缺失情况
6. ✅ 在表单中展示提取结果

**对应文件：**
- `glm4v_api.py` - API调用封装代码
- `info_extractor.py` - 信息提取和解析代码
- `api_config.json` - API配置文件（不包含真实API密钥）
- `env.example` - 环境变量配置示例（包含API密钥配置说明）
- `extraction_results.json` - 提取结果示例
- `api_test_report.md` - API测试报告（包含成功率统计）
- `GLM4V_API使用说明.md` - API使用详细说明

**功能验证：**
- ✅ API密钥配置（.env文件）
- ✅ API调用函数实现
- ✅ JSON结果解析
- ✅ 10个字段信息提取
- ✅ 错误处理机制
- ✅ 表单展示提取结果

---

### 作业五：数据核实、提交与导出系统 ✅

**功能要求：**
1. ✅ 实现可编辑表单，展示提取的证书信息
2. ✅ 用户可修改表单中的任意字段
3. ✅ 实现"保存草稿"功能，将数据存储为草稿状态
4. ✅ 实现"批量提交"功能，提交后数据不可修改
5. ✅ 管理员可查看所有用户提交的数据
6. ✅ 管理员可导出数据为CSV和Excel格式
7. ✅ 实现截止时间控制机制

**对应文件：**
- `form_handler.py` - 表单处理代码（草稿、提交、截止时间）
- `data_export.py` - 数据导出代码（CSV、Excel）
- `admin_panel.py` - 管理员面板代码
- `complete_system.py` - 完整系统主程序（命令行工具）
- `sample_export.xlsx` - 导出文件示例
- `final_report.md` - 项目总结报告

**功能验证：**
- ✅ 可编辑表单（所有字段可修改）
- ✅ 保存草稿功能
- ✅ 批量提交功能
- ✅ 提交后数据不可修改
- ✅ 管理员数据查看
- ✅ CSV导出功能
- ✅ Excel导出功能
- ✅ 截止时间控制机制

---

## 🎯 app.py 的作用

`app.py` 是**系统的主程序文件**，作用如下：

### 主要功能：
1. **整合所有功能模块**：将五个作业任务的所有功能整合到一个统一的Streamlit Web界面中
2. **用户界面实现**：提供完整的Web界面，包括：
   - 登录/注册界面
   - 证书上传界面
   - 证书预览界面
   - 信息编辑表单
   - 草稿管理界面
   - 管理员控制台
3. **业务流程控制**：实现完整的证书处理流程：
   - 用户认证 → 文件上传 → 证书预览 → 智能识别 → 信息核验 → 保存/提交
4. **权限控制**：根据用户角色（学生/教师/管理员）显示不同的功能界面
5. **数据展示**：展示用户数据、证书记录、统计数据等

### 代码结构：
- **导入模块**：导入所有功能模块（auth_system、file_upload、pdf_converter等）
- **界面函数**：实现各个页面的显示函数（show_login、show_upload_and_form等）
- **主函数**：`main()` 函数控制整个应用的流程和路由
- **状态管理**：使用 Streamlit 的 session_state 管理用户登录状态、草稿编辑状态等

### 与其他文件的关系：
- `app.py` 调用各个功能模块的函数，但不包含具体的业务逻辑
- 业务逻辑分散在各个模块文件中（如 `auth_system.py`、`file_upload.py` 等）
- `app.py` 负责将这些模块组合成完整的用户界面和业务流程

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows / Linux / macOS

### 安装步骤

1. **克隆或下载项目**
   ```bash
   cd 竞赛证书识别系统
   ```

2. **创建并激活虚拟环境（推荐）**
   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置 API 密钥（可选，用于作业四）**
   
   复制 `env.example` 为 `.env` 并配置 GLM-4V API 密钥：
   
   **Windows:**
   ```cmd
   copy env.example .env
   ```
   
   **Linux/macOS:**
   ```bash
   cp env.example .env
   ```
   
   编辑 `.env` 文件，添加你的 API 密钥：
   ```env
   GLM4V_API_KEY=your_api_key_here
   ```
   
   > 💡 如果没有配置 API 密钥，系统会提示手动填写证书信息，不影响其他功能使用。

5. **初始化数据库**
   ```bash
   python -m database --init
   ```
   
   这将创建 `data/app.db` 数据库文件，并创建默认管理员账号：
   - **账号**：`admin`
   - **密码**：`Admin@123`

6. **运行应用**
   ```bash
   streamlit run app.py
   ```
   
   应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

---

## 📁 项目结构

```
竞赛证书识别系统/
├── app.py                      # 主程序文件（整合所有功能模块）
│
├── 作业一：用户注册与登录
│   ├── auth_system.py          # 用户认证系统（注册、登录、密码管理）
│   ├── user_import.py          # Excel批量导入用户
│   ├── database.py             # 数据库模型和会话管理
│   ├── init_db.sql             # 数据库初始化SQL脚本
│   └── sample_users.xlsx       # 用户导入模板和测试数据
│
├── 作业二：文件上传与格式验证
│   ├── file_upload.py          # 文件上传处理
│   ├── file_validator.py       # 文件格式和大小验证
│   └── test_files/             # 测试用的样本文件
│
├── 作业三：证书预览与图片处理
│   ├── pdf_converter.py        # PDF转图片（支持PyMuPDF和pdf2image）
│   ├── image_processor.py      # 图片处理（旋转、缩放、Base64编码）
│   ├── preview_demo.py         # 证书预览演示页面
│   └── sample_certificates/     # 示例证书文件
│
├── 作业四：GLM-4V API集成
│   ├── glm4v_api.py            # GLM-4V API调用封装
│   ├── info_extractor.py       # 信息提取和规范化
│   ├── api_config.json          # API配置文件示例
│   ├── extraction_results.json  # 提取结果示例
│   └── GLM4V_API使用说明.md     # API使用详细说明
│
├── 作业五：数据核实与导出
│   ├── form_handler.py         # 表单处理（草稿、提交、截止时间）
│   ├── data_export.py          # 数据导出（CSV、Excel）
│   ├── admin_panel.py          # 管理员面板功能
│   ├── complete_system.py      # 完整系统主程序（命令行工具）
│   └── sample_export.xlsx      # 导出文件示例
│
├── data/                       # 数据库目录
│   └── app.db                 # SQLite数据库文件
├── uploads/                    # 上传文件目录
│
├── requirements.txt            # Python依赖清单
├── .env                        # 环境变量配置（需自行创建）
├── env.example                 # 环境变量配置示例
├── .gitignore                  # Git忽略文件
├── final_report.md             # 项目总结报告
└── README.md                   # 项目说明文档（本文件）
```

---

## ✨ 系统功能概览

### 🔐 用户管理（作业一）
- 用户注册/登录（学生13位学号、教师8位工号）
- 角色权限控制（RBAC）
- 批量导入用户（Excel）
- 密码管理（修改、重置）

### 📄 文件管理（作业二）
- 文件上传（PDF、JPG、PNG、JPEG，最大10MB）
- 格式和大小验证
- 文件存储和数据库记录

### 🖼️ 证书预览（作业三）
- PDF转图片（提取第一页）
- 图片预览和显示
- 图片处理（旋转、缩放）
- Base64编码转换

### 🤖 AI智能识别（作业四）
- GLM-4V API集成
- 自动提取10个字段信息
- 信息规范化处理
- 错误处理和容错机制

### 📊 数据管理（作业五）
- 可编辑表单
- 草稿保存和编辑
- 批量提交
- 数据查看和统计
- 数据导出（CSV、Excel）
- 截止时间控制

---

## 📝 依赖说明

主要依赖包（详见 `requirements.txt`）：

- `streamlit>=1.28.0` - Web应用框架
- `sqlmodel>=0.0.14` - ORM框架
- `bcrypt>=4.0.1` - 密码加密
- `PyMuPDF>=1.23.0` - PDF处理（推荐）
- `pdf2image>=1.16.0` - PDF转图片（备选）
- `Pillow>=10.0.0` - 图片处理
- `pandas>=2.0.0` - 数据处理
- `requests>=2.31.0` - HTTP请求（GLM-4V API）
- `python-dotenv>=1.0.0` - 环境变量管理
- `openpyxl>=3.1.0` - Excel文件处理

---

## 🔧 常见问题

### Q: PDF 转图片失败怎么办？

**A:** 系统优先使用 PyMuPDF（推荐），如果失败会自动尝试 pdf2image。如果都失败：

1. **推荐方案**：安装 PyMuPDF（最简单，无需外部依赖）
   ```bash
   pip install PyMuPDF
   ```

2. **备选方案**：使用 pdf2image（需要安装 Poppler）
   - Windows: 下载 [Poppler Windows](https://github.com/oschwartz10612/poppler-windows/releases)
   - Linux: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

3. **临时方案**：直接上传图片格式（JPG/PNG）的证书文件

### Q: GLM-4V API 识别失败怎么办？

**A:** 
- 检查 `.env` 文件中的 API 密钥是否正确
- 检查网络连接和 API 配额
- 如果 API 调用失败，可以手动填写证书信息

### Q: 如何批量导入用户？

**A:** 
1. 准备 Excel 文件，包含列：`account_id`, `name`, `role`, `department`, `email`（可选：`password`）
2. 管理员登录后，在"管理控制台"上传 Excel 文件
3. 选择是否更新已存在账号
4. 点击"开始导入"

### Q: 草稿可以编辑吗？

**A:** 可以。在"我的草稿"页面点击"编辑"按钮，可以修改所有字段并重新保存。

---

## 📚 相关文档

- [GLM-4V API 使用说明](./GLM4V_API使用说明.md) - 详细的 API 配置和使用指南
- [数据库初始化脚本](./init_db.sql) - 数据库表结构参考
- [项目总结报告](./final_report.md) - 项目完整总结

---

## 🔒 安全说明

- 密码使用 bcrypt 加密存储
- 文件上传有格式和大小限制
- 用户权限通过 RBAC 控制
- API 密钥存储在 `.env` 文件中，不应提交到版本控制

---

## 📄 许可证

本项目仅供学习和研究使用。

---

**最后更新**：2025-12-28

