import datetime
import os
import sqlite3

from app.crypto_utils import decrypt_password, encrypt_password


DB_DIR = os.path.join(os.path.expanduser("~"), ".password_manager")
DB_FILE = os.path.join(DB_DIR, "passwords.db")
_DB_INITIALIZED = False


def _get_conn():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    global _DB_INITIALIZED
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL,
            url TEXT DEFAULT "",
            username TEXT DEFAULT "",
            encrypted_password BLOB NOT NULL,
            note TEXT DEFAULT "",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()
    _DB_INITIALIZED = True


def ensure_initialized():
    if not _DB_INITIALIZED:
        init_db()


def add_password(site_name, url, username, plain_password, note=""):
    ensure_initialized()
    encrypted = encrypt_password(plain_password)
    now = datetime.datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        "INSERT INTO passwords (site_name, url, username, encrypted_password, note, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (site_name, url, username, encrypted, note, now, now),
    )
    conn.commit()
    conn.close()


def update_password(record_id, site_name, url, username, plain_password=None, note=""):
    ensure_initialized()
    now = datetime.datetime.now().isoformat()
    conn = _get_conn()
    if plain_password is not None:
        encrypted = encrypt_password(plain_password)
        conn.execute(
            "UPDATE passwords SET site_name=?, url=?, username=?, encrypted_password=?, note=?, updated_at=? WHERE id=?",
            (site_name, url, username, encrypted, note, now, record_id),
        )
    else:
        conn.execute(
            "UPDATE passwords SET site_name=?, url=?, username=?, note=?, updated_at=? WHERE id=?",
            (site_name, url, username, note, now, record_id),
        )
    conn.commit()
    conn.close()


def delete_password(record_id):
    ensure_initialized()
    conn = _get_conn()
    conn.execute("DELETE FROM passwords WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


def get_all_passwords(keyword=""):
    ensure_initialized()
    conn = _get_conn()
    if keyword:
        rows = conn.execute(
            "SELECT id, site_name, url, username, encrypted_password, note, created_at, updated_at FROM passwords WHERE site_name LIKE ? OR username LIKE ? ORDER BY updated_at DESC",
            (f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, site_name, url, username, encrypted_password, note, created_at, updated_at FROM passwords ORDER BY updated_at DESC"
        ).fetchall()
    conn.close()
    result = []
    for row in rows:
        record = dict(row)
        try:
            record["plain_password"] = decrypt_password(record["encrypted_password"])
        except FileNotFoundError:
            record["plain_password"] = "[缺少密钥文件]"
        except Exception:
            record["plain_password"] = "[解密失败]"
        result.append(record)
    return result


def get_password_by_id(record_id):
    ensure_initialized()
    conn = _get_conn()
    row = conn.execute("SELECT * FROM passwords WHERE id=?", (record_id,)).fetchone()
    conn.close()
    if row:
        record = dict(row)
        try:
            record["plain_password"] = decrypt_password(record["encrypted_password"])
        except FileNotFoundError:
            record["plain_password"] = "[缺少密钥文件]"
        except Exception:
            record["plain_password"] = "[解密失败]"
        return record
    return None


def get_record_count():
    ensure_initialized()
    conn = _get_conn()
    count = conn.execute("SELECT COUNT(*) FROM passwords").fetchone()[0]
    conn.close()
    return count


def export_all_data():
    """导出所有记录（解密后），用于备份"""
    records = get_all_passwords()
    return [
        {
            "site_name": record["site_name"],
            "url": record["url"],
            "username": record["username"],
            "password": record["plain_password"],
            "note": record["note"],
        }
        for record in records
    ]


def import_records(records):
    """批量导入记录列表"""
    ensure_initialized()
    for record in records:
        add_password(
            site_name=record["site_name"],
            url=record.get("url", ""),
            username=record.get("username", ""),
            plain_password=record.get("password", ""),
            note=record.get("note", ""),
        )
