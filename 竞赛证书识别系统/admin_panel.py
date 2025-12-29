"""
管理员面板工具函数（供 Streamlit 管理界面或 CLI 使用）
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from database import get_session, Certificate, SystemConfig
from sqlmodel import select
from data_export import export_to_csv, export_to_excel


def list_submissions(status: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_session() as session:
        if status:
            rows = session.exec(select(Certificate).where(Certificate.status == status)).all()
        else:
            rows = session.exec(select(Certificate)).all()
        return [r.dict() for r in rows]


def set_deadline(iso_datetime: str, updated_by: Optional[int] = None) -> bool:
    with get_session() as session:
        cfg = session.exec(select(SystemConfig).where(SystemConfig.config_key == "submission_deadline")).first()
        if cfg:
            cfg.config_value = iso_datetime
            cfg.updated_at = __import__("datetime").datetime.utcnow()
            cfg.updated_by = updated_by
            session.add(cfg)
        else:
            cfg = SystemConfig(config_key="submission_deadline", config_value=iso_datetime, description="Submission cutoff (ISO datetime)", updated_by=updated_by)
            session.add(cfg)
        session.commit()
    return True


def get_deadline() -> Optional[str]:
    with get_session() as session:
        cfg = session.exec(select(SystemConfig).where(SystemConfig.config_key == "submission_deadline")).first()
        return cfg.config_value if cfg else None


def export_all_csv(path: str, status: Optional[str] = "submitted") -> str:
    return export_to_csv(path, status=status)


def export_all_excel(path: str, status: Optional[str] = "submitted") -> str:
    return export_to_excel(path, status=status)
