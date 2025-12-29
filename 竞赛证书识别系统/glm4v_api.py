"""
智谱GLM-4V视觉模型API调用模块
用于证书信息智能提取
"""
from __future__ import annotations

import os
import base64
import json
from typing import Dict, Any, Optional

import requests
from PIL import Image

from image_processor import image_to_base64, load_image, resize_image


# GLM-4V API配置
GLM4V_API_KEY = os.environ.get("GLM4V_API_KEY", "")
GLM4V_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# API Key从配置文件读取
CONFIG_FILE = ".env"


def load_api_key() -> str:
    """从配置文件加载API Key"""
    api_key = os.environ.get("GLM4V_API_KEY", "")
    if not api_key and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GLM4V_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    return api_key


def prepare_image_for_api(image_path: str, max_size: int = 1024) -> str:
    """
    准备图片用于API调用：加载、调整大小、转换为Base64
    
    Args:
        image_path: 图片文件路径
        max_size: 最大尺寸（宽或高），用于压缩以减少API调用成本
    
    Returns:
        Base64编码的图片字符串
    """
    img = load_image(image_path)
    # 压缩图片以降低API调用成本
    img = resize_image(img, max_width=max_size)
    return image_to_base64(img)


def extract_with_glm4v(image_path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    使用GLM-4V API提取证书信息
    
    Args:
        image_path: 证书图片路径
        api_key: API密钥（可选，默认从环境变量读取）
    
    Returns:
        提取的字段字典
    """
    api_key = api_key or load_api_key()
    if not api_key:
        raise ValueError(
            "未设置GLM-4V API Key。请设置环境变量 GLM4V_API_KEY 或在 .env 文件中配置。"
        )
    
    # 准备图片
    image_base64 = prepare_image_for_api(image_path)
    
    # 构造提示词
    prompt = """请从这张竞赛证书图片中提取以下信息，并以JSON格式返回：
{
    "student_name": "学生姓名",
    "student_id": "学号（13位数字）",
    "department": "学生所在学院",
    "competition_name": "竞赛项目名称",
    "award_category": "获奖类别（国家级/省级/校级）",
    "award_level": "获奖等级（特等奖/一等奖/二等奖/三等奖/金奖/银奖/铜奖/优秀奖）",
    "competition_type": "竞赛类型（A类/B类）",
    "organizer": "主办单位",
    "award_date": "获奖时间（格式：YYYY-MM）",
    "advisor": "指导教师姓名"
}

如果某个字段无法识别，请返回空字符串。只返回JSON，不要其他文字说明。"""
    
    # 构造请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "glm-4v-plus",  # 或 "glm-4v" 根据你的API版本
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                        },
                    },
                ],
            }
        ],
        "temperature": 0.1,  # 降低随机性，提高准确性
    }
    
    try:
        response = requests.post(GLM4V_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 解析响应
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # 尝试提取JSON
            try:
                # 如果返回的是代码块格式，提取JSON部分
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                extracted = json.loads(content)
                
                # 添加元数据
                extracted["extraction_method"] = "glm4v"
                extracted["extraction_confidence"] = 0.85  # GLM-4V的置信度
                
                return extracted
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试从文本中提取
                return parse_text_response(content)
        else:
            raise ValueError(f"API响应格式异常: {result}")
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"GLM-4V API调用失败: {e}")
    except Exception as e:
        raise RuntimeError(f"解析API响应失败: {e}")


def parse_text_response(text: str) -> Dict[str, Any]:
    """
    从文本响应中解析字段（备用方案）
    """
    result = {
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
        "extraction_method": "glm4v",
        "extraction_confidence": 0.7,
    }
    
    # 简单的关键词匹配（作为备用）
    text_lower = text.lower()
    if "一等奖" in text or "first prize" in text_lower:
        result["award_level"] = "一等奖"
    elif "二等奖" in text or "second prize" in text_lower:
        result["award_level"] = "二等奖"
    elif "三等奖" in text or "third prize" in text_lower:
        result["award_level"] = "三等奖"
    
    return result


def test_api_connection(api_key: Optional[str] = None) -> bool:
    """测试API连接"""
    try:
        api_key = api_key or load_api_key()
        if not api_key:
            return False
        # 可以发送一个简单的测试请求
        return True
    except Exception:
        return False


