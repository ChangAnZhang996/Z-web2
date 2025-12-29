"""
User batch import from Excel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd
import bcrypt
from sqlmodel import select

from auth_system import validate_account_id, validate_password, infer_role_by_length
from database import User, get_session


@dataclass
class ImportStats:
    success: int = 0
    failed: int = 0
    updated: int = 0
    skipped: int = 0
    details: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []


def load_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    required_cols = ["account_id", "name", "role", "department", "email"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Excel缺少必填列: {', '.join(missing)}")
    return df


def import_users_from_excel(path: str, update_existing: bool = False, default_password: str = "Welcome123") -> ImportStats:
    stats = ImportStats()
    df = load_excel(path)
    with get_session() as session:
        for _, row in df.iterrows():
            try:
                account_id = str(row["account_id"]).strip()
                name = str(row["name"]).strip()
                role = str(row["role"]).strip().lower()
                department = str(row["department"]).strip()
                email = str(row["email"]).strip()
                password = str(row["password"]).strip() if "password" in row and not pd.isna(row["password"]) else default_password

                role = role or infer_role_by_length(account_id) or ""
                if role not in {"student", "teacher", "admin"}:
                    raise ValueError("角色无效，应为 student/teacher/admin")
                if not validate_account_id(account_id, role):
                    raise ValueError("学(工)号格式不符合要求")
                if not validate_password(password):
                    raise ValueError("密码不符合复杂度要求")

                existing = session.exec(select(User).where(User.account_id == account_id)).first()
                if existing:
                    if update_existing:
                        existing.name = name
                        existing.role = role
                        existing.department = department
                        existing.email = email
                        existing.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                        session.add(existing)
                        session.commit()
                        stats.updated += 1
                        stats.details.append(f"{account_id}: updated")
                    else:
                        stats.skipped += 1
                        stats.details.append(f"{account_id}: skipped (exists)")
                    continue

                pwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                user = User(
                    account_id=account_id,
                    name=name,
                    role=role,
                    department=department,
                    email=email,
                    password_hash=pwd_hash,
                    created_by="admin_import",
                )
                session.add(user)
                session.commit()
                stats.success += 1
                stats.details.append(f"{account_id}: created")
            except Exception as e:
                stats.failed += 1
                stats.details.append(f"{row.get('account_id', 'unknown')}: failed - {str(e)}")
    return stats


def generate_report(stats: ImportStats) -> str:
    lines = [
        "## 导入报告",
        f"- ✅ 成功创建: {stats.success}",
        f"- 🔄 更新: {stats.updated}",
        f"- ⏭️ 跳过: {stats.skipped}",
        f"- ❌ 失败: {stats.failed}",
    ]
    if stats.details:
        lines.append("\n### 详细信息")
        lines.extend([f"- {d}" for d in stats.details[:20]])  # Limit to 20 items
    return "\n".join(lines)


