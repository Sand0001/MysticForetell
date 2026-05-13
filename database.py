"""
SQLite 数据库管理：用户系统 + 占卜日志
"""
import sqlite3
import bcrypt
import uuid
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mystic.db")

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nickname TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        last_login TEXT
    )
    """)
    
    # 占卜日志表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS divination_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT DEFAULT '游客',
        question TEXT,
        spread_type TEXT,
        cards_json TEXT,
        interpretation TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # 用户 session 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()

# ========== 用户操作 ==========

def register_user(username: str, password: str, nickname: str = "") -> dict:
    """注册新用户"""
    conn = get_db()
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute(
            "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)",
            (username, password_hash, nickname or username)
        )
        conn.commit()
        return {"success": True, "message": "注册成功"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "该用户名已被注册"}
    finally:
        conn.close()

def login_user(username: str, password: str) -> dict:
    """用户登录，返回 session token"""
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            return {"success": False, "message": "用户名不存在"}
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return {"success": False, "message": "密码错误"}
        
        # 生成 session token
        token = str(uuid.uuid4())
        conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user['id']))
        conn.execute("UPDATE users SET last_login = datetime('now', 'localtime') WHERE id = ?", (user['id'],))
        conn.commit()
        
        return {
            "success": True,
            "token": token,
            "nickname": user['nickname'] or user['username'],
            "username": user['username']
        }
    finally:
        conn.close()

def get_user_by_token(token: str) -> dict | None:
    """通过 token 获取用户信息"""
    conn = get_db()
    try:
        row = conn.execute("""
            SELECT u.id, u.username, u.nickname 
            FROM sessions s JOIN users u ON s.user_id = u.id 
            WHERE s.token = ?
        """, (token,)).fetchone()
        if row:
            return {"id": row['id'], "username": row['username'], "nickname": row['nickname']}
        return None
    finally:
        conn.close()

def logout_user(token: str):
    """退出登录"""
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# ========== 占卜日志 ==========

def save_divination_log(user_id: int | None, username: str, question: str, 
                        spread_type: str, cards: list, interpretation: str):
    """保存占卜记录"""
    conn = get_db()
    conn.execute(
        """INSERT INTO divination_logs 
           (user_id, username, question, spread_type, cards_json, interpretation) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, username, question, spread_type, json.dumps(cards, ensure_ascii=False), interpretation)
    )
    conn.commit()
    conn.close()

def get_user_logs(user_id: int, limit: int = 20) -> list:
    """获取用户的占卜历史"""
    conn = get_db()
    rows = conn.execute(
        """SELECT question, spread_type, cards_json, interpretation, created_at 
           FROM divination_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 启动时初始化
init_db()
