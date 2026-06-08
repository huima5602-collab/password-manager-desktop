import os
import sqlite3

from cryptography.fernet import Fernet


KEY_DIR = os.path.join(os.path.expanduser("~"), ".password_manager")
KEY_FILE = os.path.join(KEY_DIR, "key.key")
SALT_FILE = os.path.join(KEY_DIR, "salt.salt")
DB_FILE = os.path.join(KEY_DIR, "passwords.db")


def _ensure_dir():
    os.makedirs(KEY_DIR, exist_ok=True)


def _database_has_records():
    if not os.path.exists(DB_FILE):
        return False
    try:
        conn = sqlite3.connect(DB_FILE)
        row = conn.execute("SELECT COUNT(*) FROM passwords").fetchone()
        conn.close()
        return bool(row and row[0] > 0)
    except sqlite3.Error:
        return False


def _load_or_create_key(create_if_missing):
    _ensure_dir()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
        Fernet(key)
        return key
    if _database_has_records():
        raise FileNotFoundError("缺少密钥文件，无法解密已有数据。")
    if not create_if_missing:
        raise FileNotFoundError("缺少密钥文件。")
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def get_cipher(create_if_missing=False):
    key = _load_or_create_key(create_if_missing=create_if_missing)
    return Fernet(key)


def encrypt_password(plain_password: str) -> bytes:
    cipher = get_cipher(create_if_missing=True)
    return cipher.encrypt(plain_password.encode("utf-8"))


def decrypt_password(encrypted_password: bytes) -> str:
    cipher = get_cipher()
    return cipher.decrypt(encrypted_password).decode("utf-8")
