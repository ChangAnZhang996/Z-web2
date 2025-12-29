"""
数据导出：CSV 和 Excel 导出工具
"""
from __future__ import annotations
from typing import Optional
import pandas as pd
from database import get_session, Certificate
from sqlmodel import select


def _query_submissions(status: Optional[str] = "submitted"):
    with get_session() as session:
        if status:
            rows = session.exec(select(Certificate).where(Certificate.status == status)).all()
        else:
            rows = session.exec(select(Certificate)).all()
        records = [r.dict() for r in rows]
    return records


def export_to_csv(path: str, status: Optional[str] = "submitted") -> str:
    records = _query_submissions(status)
    df = pd.DataFrame(records)
    # 简化列顺序
    cols = [
        "cert_id", "submitter_id", "submitter_role", "student_id", "student_name", "department",
        "competition_name", "award_category", "award_level", "competition_type", "organizer", "award_date",
        "advisor", "file_path", "status", "submitted_at",
    ]
    df = df[[c for c in cols if c in df.columns]]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def export_to_excel(path: str, status: Optional[str] = "submitted") -> str:
    records = _query_submissions(status)
    df = pd.DataFrame(records)
    # 使用 pandas 导出为 Excel
    df.to_excel(path, index=False)
    return path
