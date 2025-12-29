# 智谱GLM-4V API 使用说明

## 一、获取API密钥

1. **注册智谱AI账号**
   - 访问智谱AI开放平台：https://open.bigmodel.cn/
   - 注册并登录账号

2. **创建API密钥**
   - 登录后进入"API Keys"或"密钥管理"页面
   - 点击"创建新密钥"
   - 复制生成的API Key（格式类似：`sk-xxxxxxxxxxxxx`）
   - ⚠️ **重要**：请妥善保管API Key，不要泄露给他人

3. **查看API文档**
   - 访问：https://open.bigmodel.cn/dev/api#glm-4v
   - 了解API调用方式、计费规则和限制

## 二、配置API密钥

### 方法1：环境变量（推荐）

**Windows PowerShell:**
```powershell
$env:GLM4V_API_KEY="sk-your-api-key-here"
```

**Windows CMD:**
```cmd
set GLM4V_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export GLM4V_API_KEY="sk-your-api-key-here"
```

### 方法2：创建.env文件（项目根目录）

在项目根目录创建 `.env` 文件，内容如下：
```
GLM4V_API_KEY=sk-your-api-key-here
```

⚠️ **注意**：`.env` 文件包含敏感信息，不要提交到Git仓库。建议添加到 `.gitignore`。

### 方法3：永久设置（Windows）

1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"用户变量"中点击"新建"
5. 变量名：`GLM4V_API_KEY`
6. 变量值：你的API密钥
7. 点击"确定"保存

## 三、API调用说明

### 功能说明

系统使用GLM-4V视觉大模型自动识别证书图片中的以下信息：

- **学生姓名**：证书上的学生姓名
- **学号**：13位数字学号
- **学院**：学生所在学院
- **竞赛项目**：竞赛名称
- **获奖类别**：国家级/省级
- **获奖等级**：特等奖/一等奖/二等奖/三等奖/金奖/银奖/铜奖/优秀奖
- **竞赛类型**：A类/B类
- **主办单位**：竞赛主办方
- **获奖时间**：格式YYYY-MM
- **指导教师**：指导教师姓名

### 调用流程

1. 用户上传证书文件（PDF或图片）
2. 系统将PDF转换为图片（如需要）
3. 图片自动压缩至1024px以内（降低API调用成本）
4. 图片转换为Base64编码
5. 调用GLM-4V API，发送图片和提取提示词
6. 解析API返回的JSON结果
7. 在表单中自动填充提取的信息
8. 用户核验并补充缺失字段

### API请求示例

```python
import requests

headers = {
    "Authorization": "Bearer sk-your-api-key",
    "Content-Type": "application/json"
}

payload = {
    "model": "glm-4v-plus",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "提取证书信息..."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
            ]
        }
    ]
}

response = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers=headers,
    json=payload
)
```

## 四、代码文件说明

### `glm4v_api.py`

主要功能模块，包含：

- `load_api_key()`: 从环境变量或配置文件加载API密钥
- `prepare_image_for_api()`: 准备图片（压缩、Base64编码）
- `extract_with_glm4v()`: 调用GLM-4V API提取证书信息
- `parse_text_response()`: 备用解析函数（JSON解析失败时使用）
- `test_api_connection()`: 测试API连接

### `info_extractor.py`

信息规范化模块，包含：

- `extract_info()`: 调用GLM-4V并规范化输出字段
- `normalize_date()`: 规范化日期格式为YYYY-MM

### `app.py` 中的集成

- `extract_certificate_fields()`: 已更新为调用GLM-4V API
- 图片预览大小：从1200px调整为800px，便于一屏显示

## 五、使用步骤

### 1. 安装依赖

确保已安装所需依赖：
```bash
pip install -r requirements.txt
```

主要依赖：
- `requests`: HTTP请求库
- `Pillow`: 图片处理
- `streamlit`: Web界面

### 2. 配置API密钥

按照"二、配置API密钥"中的方法设置API Key。

### 3. 测试配置

运行测试脚本：
```bash
python test_glm4v.py
```

### 4. 运行应用

```bash
streamlit run app.py
```

### 5. 使用智能识别

1. 登录系统（学生或教师账号）
2. 点击"上传证书并识别"
3. 选择证书文件（PDF或图片）
4. 系统自动调用GLM-4V识别信息
5. 核验并补充缺失字段
6. 保存草稿或提交

## 六、故障排查

### 问题1：提示"未设置GLM-4V API Key"

**解决方案：**
- 检查环境变量是否设置：`echo $env:GLM4V_API_KEY`（PowerShell）
- 确认`.env`文件存在且格式正确
- 重启Streamlit应用

### 问题2：API调用失败

**可能原因：**
- API Key无效或过期
- 网络连接问题
- API服务暂时不可用
- 图片格式不支持

**解决方案：**
- 检查API Key是否正确
- 检查网络连接
- 查看API响应错误信息
- 尝试使用其他格式的证书图片

### 问题3：识别结果不准确

**可能原因：**
- 证书图片质量较差
- 证书格式特殊
- 文字模糊或倾斜

**解决方案：**
- 上传清晰、正面的证书图片
- 手动核验并修正识别结果
- 补充缺失字段

### 问题4：识别速度慢

**说明：**
- GLM-4V API调用需要网络请求，通常需要2-5秒
- 图片较大时会自动压缩，但首次处理可能需要时间

**优化建议：**
- 上传前压缩图片（建议宽度不超过1024px）
- 使用清晰的图片，减少API处理时间

## 七、费用说明

- GLM-4V API按调用次数和图片大小计费
- 具体价格请查看：https://open.bigmodel.cn/pricing
- 建议：
  - 压缩图片至1024px以内（代码已自动处理）
  - 仅在需要时调用API（已设置演示模式作为备选）

## 八、演示模式

如果未配置API Key，系统会使用演示模式：
- 返回示例数据供测试
- 提示用户配置API Key以启用智能识别
- 用户可手动填写所有字段

## 九、技术支持

- 智谱AI官方文档：https://open.bigmodel.cn/dev/api
- 项目问题反馈：请查看项目README或联系开发者

---

**最后更新：** 2024-12-23


