"""
User registration and authentication logic.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

import bcrypt
from sqlmodel import select

from database import User, get_session


STUDENT_ID_LEN = 13
TEACHER_ID_LEN = 8


def validate_account_id(account_id: str, role: str) -> bool:
    if not account_id.isdigit():
        return False
    if role == "student":
        return len(account_id) == STUDENT_ID_LEN
    if role == "teacher":
        return len(account_id) == TEACHER_ID_LEN
    if role == "admin":
        return len(account_id) >= 4
    return False


def infer_role_by_length(account_id: str) -> Optional[str]:
    if account_id.isdigit() and len(account_id) == STUDENT_ID_LEN:
        return "student"
    if account_id.isdigit() and len(account_id) == TEACHER_ID_LEN:
        return "teacher"
    return None


def validate_password(password: str) -> bool:
    return bool(len(password) >= 8 and re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password))


def register_user(account_id: str, name: str, password: str, role: Optional[str], department: str, email: str) -> Tuple[bool, str]:
    inferred_role = role or infer_role_by_length(account_id)
    if inferred_role is None:
        return False, "无法根据学(工)号确定角色，请检查位数。"
    if not validate_account_id(account_id, inferred_role):
        return False, f"{'学号' if inferred_role=='student' else '工号'}位数不正确。"
    if not validate_password(password):
        return False, "密码需至少8位，包含字母和数字。"

    with get_session() as session:
        exists = session.exec(select(User).where(User.account_id == account_id)).first()
        if exists:
            return False, "该学(工)号已存在。"
        email_used = session.exec(select(User).where(User.email == email)).first()
        if email_used:
            return False, "该邮箱已被注册。"

        pwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(
            account_id=account_id,
            name=name,
            role=inferred_role,
            department=department,
            email=email,
            password_hash=pwd_hash,
            created_by="self_register",
        )
        session.add(user)
        session.commit()
        return True, "注册成功"


def authenticate_user(account_id: str, password: str) -> Tuple[bool, Optional[User], str]:
    with get_session() as session:
        user = session.exec(select(User).where(User.account_id == account_id)).first()
        if not user:
            return False, None, "账号不存在，请先注册或联系管理员。"
        if not user.is_active:
            return False, None, "账号已被禁用，请联系管理员。"
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return False, None, "密码错误。"
        return True, user, "登录成功"


def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
    """用户修改自己的密码"""
    if not validate_password(new_password):
        return False, "新密码需至少8位，包含字母和数字。"
    
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return False, "用户不存在。"
        if not bcrypt.checkpw(old_password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return False, "原密码错误。"
        
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password_hash = new_hash
        session.add(user)
        session.commit()
        return True, "密码修改成功"


def admin_reset_password(admin_user_id: int, target_account_id: str, new_password: str = "123456") -> Tuple[bool, str]:
    """管理员重置用户密码（默认重置为123456，管理员重置时跳过密码复杂度验证）"""
    with get_session() as session:
        admin = session.get(User, admin_user_id)
        if not admin or admin.role != "admin":
            return False, "权限不足，仅管理员可重置密码。"
        
        target_user = session.exec(select(User).where(User.account_id == target_account_id)).first()
        if not target_user:
            return False, "目标用户不存在。"
        
        if target_user.role == "admin":
            return False, "不能重置管理员密码。"
        
        # 管理员重置密码时跳过密码复杂度验证，允许设置为简单密码（如123456）
        # 但至少需要6位字符
        if len(new_password) < 6:
            return False, "密码至少需要6位字符。"
        
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        target_user.password_hash = new_hash
        session.add(target_user)
        session.commit()
        return True, f"密码已重置为：{new_password}"

