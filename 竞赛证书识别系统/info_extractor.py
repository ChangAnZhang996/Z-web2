"""
信息提取器：封装对 GLM-4V 的调用并规范化输出字段
"""
from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime

from glm4v_api import extract_with_glm4v

REQUIRED_FIELDS = [
    "department",
    "competition_name",
    "student_id",
    "student_name",
    "award_category",
    "award_level",
    "competition_type",
    "organizer",
    "award_date",
    "advisor",
]


def normalize_date(value: str) -> str:
    """尝试将日期规范为 YYYY-MM 或原样返回空串"""
    if not value:
        return ""
    try:
        # 支持 YYYY-MM 或 YYYY年MM月 或 YYYY/MM/DD 等简单格式
        value = value.strip()
        if "年" in value:
            parts = value.split("年")
            year = parts[0]
            month = parts[1].replace("月", "").split(" ")[0]
            return f"{int(year):04d}-{int(month):02d}"
        if "/" in value:
            parts = value.split("/")
            return f"{int(parts[0]):04d}-{int(parts[1]):02d}"
        if "-" in value:
            parts = value.split("-")
            return f"{int(parts[0]):04d}-{int(parts[1]):02d}"
        # 仅年份
        if len(value) == 4 and value.isdigit():
            return f"{value}-01"
    except Exception:
        return ""
    return value


def extract_info(image_path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    调用 GLM-4V 并规范化输出，保证返回包含所有 REQUIRED_FIELDS 的字典。
    当 API 调用失败或某些字段缺失时，使用空字符串占位并记录状态信息。
    """
    result: Dict[str, Any] = {k: "" for k in REQUIRED_FIELDS}
    result.update({"extraction_method": "", "extraction_confidence": 0.0, "file_name": ""})

    try:
        raw = extract_with_glm4v(image_path, api_key=api_key)
    except Exception as exc:
        # 记录失败信息以便上层展示
        result.update({"extraction_method": "glm4v_failed", "extraction_confidence": 0.0})
        result["_error"] = str(exc)
        return result

    # GLM 返回的字段名可能与我们预期一致；尽量兼容常见别名
    mapping_candidates = {
        "department": ["department", "院系", "学院", "school", "college"],
        "competition_name": ["competition_name", "竞赛项目", "competition", "project"],
        "student_id": ["student_id", "学号", "id"],
        "student_name": ["student_name", "姓名", "name"],
        "award_category": ["award_category", "获奖类别"],
        "award_level": ["award_level", "获奖等级"],
        "competition_type": ["competition_type", "竞赛类型"],
        "organizer": ["organizer", "主办单位", "organiser"],
        "award_date": ["award_date", "获奖时间", "date"],
        "advisor": ["advisor", "指导教师", "导师"] ,
    }

    # 将raw中的键全部小写映射以便匹配
    raw_lower = {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            raw_lower[k.lower()] = v
    # 直接尝试用常见键
    for key, candidates in mapping_candidates.items():
        for c in candidates:
            cv = raw.get(c)
            if cv:
                result[key] = str(cv).strip()
                break
            cv2 = raw_lower.get(str(c).lower())
            if cv2:
                result[key] = str(cv2).strip()
                break

    # 一些字段需要进一步规范化
    result["award_date"] = normalize_date(result.get("award_date", ""))

    # 元数据
    result["extraction_method"] = raw.get("extraction_method", "glm4v") if isinstance(raw, dict) else "glm4v"
    try:
        conf = raw.get("extraction_confidence", None)
        if conf is None and isinstance(raw, dict) and "confidence" in raw:
            conf = raw.get("confidence")
        result["extraction_confidence"] = float(conf) if conf is not None else 0.0
    except Exception:
        result["extraction_confidence"] = 0.0

    # 附加原始字段备查
    result["_raw_response"] = raw
    return result
