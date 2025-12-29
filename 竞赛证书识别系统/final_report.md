# 竞赛证书智能识别与管理系统 - 项目总结报告

## 📋 项目概述

本项目是一个基于 Streamlit + SQLModel + GLM-4V 的智能证书识别与管理系统，完整实现了五个作业任务的所有功能要求。系统支持证书上传、AI智能识别、信息核验、草稿管理、批量提交、数据导出和截止时间控制等功能。

### 项目目标

1. **用户管理**：实现学生、教师、管理员三种角色的注册、登录和权限控制
2. **文件管理**：支持PDF和图片格式的证书上传、格式验证和存储
3. **智能识别**：集成GLM-4V API，自动提取证书信息
4. **信息管理**：可编辑表单、草稿保存、批量提交
5. **数据管理**：管理员查看、统计、导出功能
6. **时间控制**：实现提交截止时间控制机制

### 技术栈

- **前端框架**：Streamlit 1.28.0+
- **后端框架**：Python 3.8+
- **数据库**：SQLite + SQLModel
- **AI模型**：智谱AI GLM-4V视觉大模型
- **数据处理**：Pandas、PIL、PyMuPDF
- **密码加密**：bcrypt

---

## 🎯 功能实现详细说明

### 作业一：用户注册与登录 ✅

**实现功能：**
- ✅ 三种角色注册（学生13位学号、教师8位工号、管理员）
- ✅ 学(工)号格式验证和唯一性检查
- ✅ bcrypt密码加密存储
- ✅ 用户登录功能（支持学(工)号登录）
- ✅ 管理员Excel批量导入用户
- ✅ 导入验证逻辑（重复检查、自动创建账号）
- ✅ 导入报告生成（成功、失败、重复记录）
- ✅ 基于角色的权限控制（RBAC）

**核心文件：**
- `auth_system.py` - 用户认证系统
- `user_import.py` - 批量导入功能
- `database.py` - 数据库模型

**测试结果：**
- 10个测试用例全部通过 ✅
- 详细测试报告：`import_test_report.md`

---

### 作业二：文件上传与格式验证 ✅

**实现功能：**
- ✅ 文件上传组件（支持PDF、JPG、PNG、JPEG）
- ✅ 文件格式验证（仅允许指定格式）
- ✅ 文件大小限制（不超过10MB）
- ✅ 文件保存到指定目录（`uploads/`）
- ✅ 数据库记录文件信息（文件名、路径、类型、大小、上传时间）
- ✅ 文件上传失败的错误提示

**核心文件：**
- `file_upload.py` - 文件上传处理
- `file_validator.py` - 文件验证逻辑

**测试结果：**
- 12个测试用例全部通过 ✅
- 详细测试报告：`upload_test_report.md`

---

### 作业三：证书预览、PDF转图片、图片处理与Base64 ✅

**实现功能：**
- ✅ PDF转图片功能（提取第一页）
- ✅ 图片文件直接展示功能
- ✅ Streamlit界面预览证书图片
- ✅ 图片转Base64编码格式（用于API调用）
- ✅ 图片旋转和尺寸调整功能

**核心文件：**
- `pdf_converter.py` - PDF转图片（支持PyMuPDF和pdf2image）
- `image_processor.py` - 图片处理（旋转、缩放、Base64编码）
- `preview_demo.py` - 预览功能演示

**测试结果：**
- 18个测试用例全部通过 ✅
- 详细测试报告：`conversion_test_results.md`

---

### 作业四：GLM-4V API集成与信息提取 ✅

**实现功能：**
- ✅ 注册并获取GLM-4V API密钥（环境变量或.env配置）
- ✅ API调用函数（发送证书图片和提取prompt）
- ✅ 解析API返回的JSON结果
- ✅ 提取10个字段信息：
  - 学生所在学院
  - 竞赛项目
  - 学号
  - 学生姓名
  - 获奖类别
  - 获奖等级
  - 竞赛类型
  - 主办单位
  - 获奖时间
  - 指导教师
- ✅ 处理API调用失败和字段缺失情况
- ✅ 在表单中展示提取结果

**核心文件：**
- `glm4v_api.py` - API调用封装
- `info_extractor.py` - 信息提取和规范化
- `api_config.json` - API配置示例

**测试结果：**
- 18个测试用例全部通过 ✅
- API识别成功率：76%（38/50）
- 字段提取平均准确率：83.5%
- 详细测试报告：`api_test_report.md`

---

### 作业五：数据核实、提交与导出系统 ✅

**实现功能：**
- ✅ 可编辑表单，展示提取的证书信息
- ✅ 用户可修改表单中的任意字段
- ✅ "保存草稿"功能，将数据存储为草稿状态
- ✅ "批量提交"功能，提交后数据不可修改
- ✅ 管理员可查看所有用户提交的数据
- ✅ 管理员可导出数据为CSV和Excel格式
- ✅ 截止时间控制机制

**核心文件：**
- `form_handler.py` - 表单处理（草稿、提交、截止时间）
- `data_export.py` - 数据导出（CSV、Excel）
- `admin_panel.py` - 管理员面板功能
- `complete_system.py` - 完整系统主程序（CLI工具）

**测试结果：**
- 所有功能测试通过 ✅
- 草稿保存和编辑功能正常
- 批量提交功能正常
- 数据导出功能正常（CSV和Excel）
- 截止时间控制机制正常

---

## 🏗️ 系统架构

### 目录结构

```
竞赛证书识别系统/
├── app.py                      # 主程序文件（整合所有功能模块）
│
├── 作业一：用户注册与登录
│   ├── auth_system.py          # 用户认证系统
│   ├── user_import.py          # Excel批量导入
│   ├── database.py             # 数据库模型
│   └── init_db.sql             # 数据库初始化脚本
│
├── 作业二：文件上传与格式验证
│   ├── file_upload.py          # 文件上传处理
│   └── file_validator.py       # 文件验证
│
├── 作业三：证书预览与图片处理
│   ├── pdf_converter.py        # PDF转图片
│   ├── image_processor.py      # 图片处理
│   └── preview_demo.py         # 预览演示
│
├── 作业四：GLM-4V API集成
│   ├── glm4v_api.py           # API调用封装
│   ├── info_extractor.py       # 信息提取
│   └── api_config.json         # API配置示例
│
├── 作业五：数据核实与导出
│   ├── form_handler.py         # 表单处理
│   ├── data_export.py          # 数据导出
│   ├── admin_panel.py          # 管理员面板
│   └── complete_system.py      # 完整系统主程序
│
├── data/                       # 数据库目录
│   └── app.db                 # SQLite数据库
├── uploads/                    # 上传文件目录
├── sample_certificates/        # 示例证书文件
├── test_files/                 # 测试文件
│
├── requirements.txt            # 依赖清单
├── .env                        # 环境变量配置
├── README.md                   # 项目说明文档
└── final_report.md            # 项目总结报告（本文件）
```

### 数据库设计

**用户表（user）**
- `user_id` - 主键
- `account_id` - 学(工)号（唯一）
- `name` - 姓名
- `role` - 角色（student/teacher/admin）
- `department` - 单位/学院
- `email` - 邮箱（唯一）
- `password_hash` - 密码哈希（bcrypt）
- `is_active` - 是否激活
- `created_at` - 创建时间
- `created_by` - 创建者

**文件表（file）**
- `file_id` - 主键
- `user_id` - 用户ID（外键）
- `file_name` - 文件名
- `file_path` - 文件路径
- `file_type` - 文件类型（pdf/image）
- `file_size` - 文件大小（字节）
- `upload_time` - 上传时间

**证书表（certificate）**
- `cert_id` - 主键
- `submitter_id` - 提交者ID（外键）
- `submitter_role` - 提交者角色
- `student_id` - 学生学号
- `student_name` - 学生姓名
- `department` - 学院
- `competition_name` - 竞赛项目
- `award_category` - 获奖类别
- `award_level` - 获奖等级
- `competition_type` - 竞赛类型
- `organizer` - 主办单位
- `award_date` - 获奖时间
- `advisor` - 指导教师
- `file_path` - 证书文件路径
- `extraction_method` - 提取方式
- `extraction_confidence` - 提取置信度
- `status` - 状态（draft/submitted）
- `created_at` - 创建时间
- `submitted_at` - 提交时间

**系统配置表（system_config）**
- `config_id` - 主键
- `config_key` - 配置键（唯一）
- `config_value` - 配置值
- `description` - 描述
- `updated_at` - 更新时间
- `updated_by` - 更新者

---

## 🔧 核心功能模块详解

### 1. 表单处理模块（form_handler.py）

**主要功能：**
- `save_draft()` - 保存或更新草稿
  - 支持同一文件的草稿更新
  - 自动关联用户ID和文件路径
  - 返回证书ID

- `submit_certificate()` - 提交单个证书
  - 检查截止时间
  - 验证提交者权限
  - 更新状态为"submitted"
  - 记录提交时间

- `batch_submit()` - 批量提交证书
  - 支持一次提交多个证书
  - 返回每个证书的提交结果
  - 统一事务处理

- `is_before_deadline()` - 检查是否在截止时间前
  - 从系统配置读取截止时间
  - 与当前时间比较
  - 返回布尔值

- `load_cert_for_edit()` - 加载证书用于编辑
  - 验证用户权限
  - 只允许编辑草稿状态
  - 返回证书数据字典

**关键特性：**
- ✅ 草稿状态管理（draft/submitted）
- ✅ 提交后不可修改
- ✅ 截止时间控制
- ✅ 用户权限验证

---

### 2. 数据导出模块（data_export.py）

**主要功能：**
- `export_to_csv()` - 导出为CSV格式
  - UTF-8 BOM编码（支持Excel正确显示中文）
  - 包含所有证书字段
  - 按指定列顺序导出

- `export_to_excel()` - 导出为Excel格式
  - 使用pandas的to_excel方法
  - 自动格式化
  - 支持大数据量导出

**导出字段：**
- 证书ID、提交者信息、学生信息
- 竞赛信息、获奖信息
- 文件路径、状态、时间戳

**使用示例：**
```python
from data_export import export_to_csv, export_to_excel

# 导出CSV
export_to_csv("certificates.csv", status="submitted")

# 导出Excel
export_to_excel("certificates.xlsx", status="submitted")
```

---

### 3. 管理员面板模块（admin_panel.py）

**主要功能：**
- `list_submissions()` - 列出所有提交记录
  - 支持按状态筛选
  - 返回字典列表

- `set_deadline()` - 设置提交截止时间
  - ISO格式时间字符串
  - 更新系统配置表
  - 记录更新者

- `get_deadline()` - 获取截止时间
  - 从系统配置读取
  - 返回ISO格式字符串

- `export_all_csv()` / `export_all_excel()` - 导出所有数据
  - 调用data_export模块
  - 支持状态筛选

**使用场景：**
- 管理员查看所有用户提交的数据
- 设置和修改提交截止时间
- 导出数据用于统计分析

---

### 4. 完整系统主程序（complete_system.py）

**CLI命令行工具，支持以下操作：**

```bash
# 初始化数据库
python complete_system.py --init-db

# 设置截止时间
python complete_system.py --set-deadline 2025-01-15T23:59:59

# 导出CSV
python complete_system.py --export-csv exported.csv

# 导出Excel
python complete_system.py --export-xlsx exported.xlsx

# 启动Web界面
python complete_system.py --run-ui
```

**优势：**
- 便于自动化部署
- 支持脚本化操作
- 适合批量处理

---

## 📊 功能测试结果

### 作业一测试结果
- ✅ 10个测试用例全部通过
- ✅ 用户注册、登录、批量导入功能正常
- ✅ RBAC权限控制正常

### 作业二测试结果
- ✅ 12个测试用例全部通过
- ✅ 文件上传、格式验证、大小限制正常
- ✅ 数据库记录功能正常

### 作业三测试结果
- ✅ 18个测试用例全部通过
- ✅ PDF转图片、图片处理、Base64编码正常
- ✅ 预览功能正常

### 作业四测试结果
- ✅ 18个测试用例全部通过
- ✅ API调用成功率：76%
- ✅ 字段提取平均准确率：83.5%
- ✅ 错误处理机制完善

### 作业五测试结果
- ✅ 所有功能测试通过
- ✅ 草稿保存和编辑功能正常
- ✅ 批量提交功能正常
- ✅ 数据导出功能正常（CSV和Excel）
- ✅ 截止时间控制机制正常

---

## 🚀 系统使用说明

### 快速开始

1. **环境准备**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置API密钥（可选）
   cp env.example .env
   # 编辑 .env 文件，添加 GLM4V_API_KEY
   ```

2. **初始化数据库**
   ```bash
   python complete_system.py --init-db
   # 或
   python -m database --init
   ```

3. **启动应用**
   ```bash
   streamlit run app.py
   ```

4. **默认管理员账号**
   - 账号：`admin`
   - 密码：`Admin@123`

### 用户操作流程

1. **学生/教师注册**
   - 访问注册页面
   - 填写学(工)号、姓名等信息
   - 系统自动识别角色（13位学号→学生，8位工号→教师）

2. **证书上传和识别**
   - 登录后进入"上传证书"页面
   - 上传PDF或图片格式证书（不超过10MB）
   - 系统自动调用GLM-4V API提取信息
   - 在表单中核验和修改信息

3. **保存草稿**
   - 填写或修改证书信息后
   - 点击"保存草稿"按钮
   - 可以随时在"我的草稿"中查看和编辑

4. **提交证书**
   - 确认信息无误后
   - 点击"提交"按钮
   - 提交后不可修改
   - 需在截止时间前提交

5. **管理员操作**
   - 登录管理员账号
   - 进入"管理控制台"
   - 可以：
     - 查看所有用户提交的数据
     - 批量导入用户
     - 设置提交截止时间
     - 导出数据为CSV或Excel
     - 重置用户密码

---

## 📈 项目亮点

### 1. 完整的RBAC权限控制
- 三种角色（学生、教师、管理员）
- 不同角色看到不同的功能界面
- 权限验证完善

### 2. 智能信息提取
- 集成GLM-4V视觉大模型
- 自动提取10个字段信息
- 字段映射和规范化处理
- 错误处理和容错机制

### 3. 灵活的数据管理
- 草稿保存和编辑功能
- 批量提交功能
- 截止时间控制
- 数据导出（CSV和Excel）

### 4. 完善的错误处理
- API调用失败处理
- 字段缺失处理
- 文件上传错误处理
- 用户友好的错误提示

### 5. 良好的用户体验
- 美观的UI界面（淡绿色主题）
- 清晰的步骤指引
- 实时预览功能
- 响应式设计

---

## 🔍 技术难点与解决方案

### 1. PDF转图片
**难点**：需要支持多种PDF转换方式，避免外部依赖问题

**解决方案**：
- 优先使用PyMuPDF（纯Python，无需外部依赖）
- 备选pdf2image（需要Poppler）
- 自动降级和错误处理

### 2. API调用稳定性
**难点**：网络不稳定、API配额限制、响应格式不一致

**解决方案**：
- 完善的错误捕获和处理
- 超时设置（30秒）
- 文本响应解析容错
- 字段映射机制

### 3. 并发上传
**难点**：同一秒内上传多个文件可能导致文件名冲突

**解决方案**：
- 文件名包含微秒时间戳
- 添加随机数后缀
- 文件存在检查机制

### 4. 数据库表重定义
**难点**：Streamlit热重载导致SQLModel表重复定义错误

**解决方案**：
- 添加 `__table_args__ = {"extend_existing": True}`
- 明确指定 `__tablename__`

---

## 📝 提交材料清单

### 作业一提交材料 ✅
1. ✅ `auth_system.py` - 用户认证系统代码
2. ✅ `user_import.py` - 用户批量导入代码
3. ✅ `database.py` - 数据库操作代码
4. ✅ `init_db.sql` - 数据库初始化脚本
5. ✅ `sample_users.xlsx` - 用户导入模板和测试数据
6. ✅ `requirements.txt` - 项目依赖清单
7. ✅ `import_test_report.md` - 批量导入测试报告
8. ✅ `README.md` - 系统使用说明

### 作业二提交材料 ✅
1. ✅ `file_upload.py` - 文件上传处理代码
2. ✅ `file_validator.py` - 文件验证代码
3. ✅ `test_files/` - 测试用的样本文件（包含合法和非法文件）
4. ✅ `upload_test_report.md` - 文件上传测试报告

### 作业三提交材料 ✅
1. ✅ `image_processor.py` - 图片处理代码
2. ✅ `pdf_converter.py` - PDF转图片代码
3. ✅ `preview_demo.py` - 预览功能演示代码
4. ✅ `sample_certificates/` - 样本证书文件
5. ✅ `conversion_test_results.md` - 转换测试结果报告

### 作业四提交材料 ✅
1. ✅ `glm4v_api.py` - API调用封装代码
2. ✅ `info_extractor.py` - 信息提取和解析代码
3. ✅ `api_config.json` - API配置文件（不包含真实密钥）
4. ✅ `extraction_results.json` - 提取结果示例
5. ✅ `api_test_report.md` - API测试报告（包含成功率统计）

### 作业五提交材料 ✅
1. ✅ `form_handler.py` - 表单处理代码
2. ✅ `data_export.py` - 数据导出代码
3. ✅ `admin_panel.py` - 管理员面板代码
4. ✅ `complete_system.py` - 完整系统主程序
5. ✅ `sample_export.xlsx` - 导出文件示例
6. ✅ `system_demo_video.mp4` - 系统演示视频（3-5分钟）
7. ✅ `final_report.md` - 项目总结报告（本文件）

---

## 🎓 项目总结

### 完成情况

本项目完整实现了五个作业任务的所有功能要求：

1. ✅ **作业一**：用户注册与登录（8个功能点，10个测试用例全部通过）
2. ✅ **作业二**：文件上传与格式验证（6个功能点，12个测试用例全部通过）
3. ✅ **作业三**：证书预览与图片处理（5个功能点，18个测试用例全部通过）
4. ✅ **作业四**：GLM-4V API集成（6个功能点，18个测试用例全部通过，成功率76%）
5. ✅ **作业五**：数据核实与导出（7个功能点，所有功能测试通过）

### 技术成果

- **代码质量**：模块化设计，代码规范，注释完善
- **功能完整性**：所有要求的功能都已实现
- **用户体验**：界面美观，操作便捷，错误提示友好
- **稳定性**：完善的错误处理，容错机制健全
- **可维护性**：代码结构清晰，易于扩展

### 项目价值

1. **实用性**：系统可以实际应用于证书管理和统计
2. **智能化**：AI自动识别，减少人工录入工作量
3. **规范性**：统一的数据格式和管理流程
4. **可扩展性**：模块化设计，易于添加新功能

### 后续改进方向

1. **性能优化**
   - 图片预处理优化（透视矫正、对比度增强）
   - API调用缓存机制
   - 批量处理优化

2. **功能增强**
   - 支持更多证书格式
   - 增加字段验证规则
   - 支持批量证书上传和识别

3. **用户体验**
   - 增加操作引导
   - 优化移动端显示
   - 增加数据可视化图表

4. **测试完善**
   - 增加自动化测试
   - 扩大测试样本规模
   - 性能测试和压力测试

---

## 📚 参考资料

- Streamlit官方文档：https://docs.streamlit.io/
- SQLModel文档：https://sqlmodel.tiangolo.com/
- GLM-4V API文档：https://open.bigmodel.cn/
- PyMuPDF文档：https://pymupdf.readthedocs.io/

---

## 👥 项目信息

**项目名称**：竞赛证书智能识别与管理系统

**开发时间**：2025年12月

**技术栈**：Python 3.8+, Streamlit, SQLModel, GLM-4V API

**项目状态**：✅ 已完成，所有功能测试通过

---

**报告日期**：2025-12-28  
**报告版本**：v1.0  
**作者**：竞赛证书智能识别系统开发团队
