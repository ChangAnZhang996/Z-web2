"""
Database models and helpers for the certificate system.
"""
from __future__ import annotations

import argparse
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select
import bcrypt

DB_PATH = os.path.join("data", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    user_id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(unique=True, index=True)  # 学(工)号
    name: str
    role: str  # student / teacher / admin
    department: Optional[str] = None
    email: str = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="self_register")  # or admin_import


class File(SQLModel, table=True):
    __tablename__ = "file"
    __table_args__ = {"extend_existing": True}
    file_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    file_name: str
    file_path: str
    file_type: str  # pdf / image
    file_size: int  # bytes
    upload_time: datetime = Field(default_factory=datetime.utcnow)


class Certificate(SQLModel, table=True):
    __tablename__ = "certificate"
    __table_args__ = {"extend_existing": True}
    cert_id: Optional[int] = Field(default=None, primary_key=True)
    submitter_id: int = Field(foreign_key="user.user_id")
    submitter_role: str  # student / teacher
    student_id: str  # 13位学号
    student_name: str
    department: Optional[str] = None
    competition_name: Optional[str] = None
    award_category: Optional[str] = None  # 国家级/省级
    award_level: Optional[str] = None  # 特等奖/一等奖/...
    competition_type: Optional[str] = None  # A类/B类
    organizer: Optional[str] = None
    award_date: Optional[str] = None  # YYYY-MM
    advisor: Optional[str] = None
    file_path: str
    extraction_method: Optional[str] = None  # glm4v/baidu/local等
    extraction_confidence: Optional[float] = None
    status: str = Field(default="draft")  # draft / submitted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None


class SystemConfig(SQLModel, table=True):
    __tablename__ = "system_config"
    __table_args__ = {"extend_existing": True}
    config_id: Optional[int] = Field(default=None, primary_key=True)
    config_key: str = Field(unique=True, index=True)
    config_value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = Field(default=None, foreign_key="user.user_id")


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    """初始化数据库表并创建默认管理员账号"""
    SQLModel.metadata.create_all(engine)
    with get_session() as session:
        admin = session.exec(select(User).where(User.account_id == "admin")).first()
        if not admin:
            pwd_hash = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            admin = User(
                account_id="admin",
                name="Administrator",
                role="admin",
                department="Academic Affairs",
                email="admin@example.com",
                password_hash=pwd_hash,
                created_by="init",
            )
            session.add(admin)
            session.commit()
            print("管理员账号已创建：admin / Admin@123")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    args = parser.parse_args()
    if args.init:
        init_db()


