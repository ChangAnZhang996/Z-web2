"""
表单处理：保存草稿、批量提交、验证截止时间
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List, Optional

from database import get_session, Certificate, SystemConfig
from sqlmodel import select


def get_submission_deadline() -> Optional[str]:
    with get_session() as session:
        cfg = session.exec(select(SystemConfig).where(SystemConfig.config_key == "submission_deadline")).first()
        return cfg.config_value if cfg else None


def is_before_deadline() -> bool:
    val = get_submission_deadline()
    if not val:
        return True
    try:
        dl = datetime.fromisoformat(val)
        return datetime.utcnow() <= dl
    except Exception:
        return True


def save_draft(user_id: int, payload: Dict[str, Any], file_path: str) -> int:
    """保存或更新草稿，返回 cert_id"""
    with get_session() as session:
        # 尝试查找已有草稿（同一提交者、同一文件）
        existing = session.exec(
            select(Certificate).where(
                (Certificate.submitter_id == user_id) & (Certificate.file_path == file_path) & (Certificate.status == "draft")
            )
        ).first()
        if existing:
            for k, v in payload.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            existing.created_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            return existing.cert_id

        # 从payload中提取submitter_role，避免重复传递
        submitter_role = payload.pop("submitter_role", "student")
        cert = Certificate(submitter_id=user_id, submitter_role=submitter_role, file_path=file_path, status="draft", **payload)
        session.add(cert)
        session.commit()
        return cert.cert_id


def submit_certificate(cert_id: int, user_id: int) -> bool:
    """将草稿提交为正式提交，变为不可修改。返回是否提交成功"""
    if not is_before_deadline():
        return False
    with get_session() as session:
        cert = session.get(Certificate, cert_id)
        if not cert:
            return False
        # 仅允许提交者本人或管理员提交（管理员由外层权限控制）
        if cert.submitter_id != user_id:
            return False
        cert.status = "submitted"
        cert.submitted_at = datetime.utcnow()
        session.add(cert)
        session.commit()
        return True


def batch_submit(cert_ids: List[int], user_id: int) -> Dict[int, bool]:
    """批量提交多个证书（仅允许提交者本人）
    返回每个 cert_id 的提交结果映射
    """
    results: Dict[int, bool] = {}
    if not is_before_deadline():
        for cid in cert_ids:
            results[cid] = False
        return results

    with get_session() as session:
        for cid in cert_ids:
            cert = session.get(Certificate, cid)
            if not cert:
                results[cid] = False
                continue
            if cert.submitter_id != user_id:
                results[cid] = False
                continue
            cert.status = "submitted"
            cert.submitted_at = datetime.utcnow()
            session.add(cert)
            results[cid] = True
        session.commit()
    return results


def load_cert_for_edit(cert_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        cert = session.get(Certificate, cert_id)
        if not cert:
            return None
        if cert.submitter_id != user_id:
            return None
        # 只有草稿允许编辑
        if cert.status != "draft":
            return None
        data = cert.model_dump()
        return data
