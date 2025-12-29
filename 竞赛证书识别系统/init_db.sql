-- 竞赛证书智能识别与管理系统 - 数据库初始化脚本
-- 用于直接在 SQLite 中执行以创建表结构

-- 用户表
CREATE TABLE IF NOT EXISTS "user" (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL DEFAULT 'self_register'
);

CREATE INDEX IF NOT EXISTS idx_user_account_id ON "user"(account_id);
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);

-- 文件表
CREATE TABLE IF NOT EXISTS "file" (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- 证书信息表
CREATE TABLE IF NOT EXISTS "certificate" (
    cert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submitter_id INTEGER NOT NULL,
    submitter_role TEXT NOT NULL,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    department TEXT,
    competition_name TEXT,
    award_category TEXT,
    award_level TEXT,
    competition_type TEXT,
    organizer TEXT,
    award_date TEXT,
    advisor TEXT,
    file_path TEXT NOT NULL,
    extraction_method TEXT,
    extraction_confidence REAL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    FOREIGN KEY (submitter_id) REFERENCES "user"(user_id)
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS "system_config" (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES "user"(user_id)
);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON "system_config"(config_key);

-- 插入默认管理员账号（密码：Admin@123，bcrypt哈希）
-- 注意：实际使用时应该通过 database.py 的 init_db() 函数创建，因为需要 bcrypt 哈希
-- 这里仅作为参考，实际密码哈希值需要通过 Python 的 bcrypt 生成


