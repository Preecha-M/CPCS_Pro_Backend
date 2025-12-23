from __future__ import annotations

from typing import Literal, Optional
import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

ph = PasswordHasher(
    time_cost=2,
    memory_cost=102400,  # 100 MiB
    parallelism=8,
    hash_len=32,
    salt_len=16,
)

HashKind = Literal["argon2", "bcrypt", "unknown"]


def detect_hash_kind(stored_hash: str) -> HashKind:
    if not stored_hash:
        return "unknown"
    if stored_hash.startswith("$argon2"):
        return "argon2"
    if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$") or stored_hash.startswith("$2y$"):
        return "bcrypt"
    return "unknown"


def hash_password_argon2(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    kind = detect_hash_kind(stored_hash)

    if kind == "argon2":
        try:
            return ph.verify(stored_hash, password)
        except (VerifyMismatchError, InvalidHash):
            return False

    if kind == "bcrypt":
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ValueError:
            # bcrypt จะ throw ถ้า password > 72 bytes (ของเก่าแก้ไม่ได้)
            return False

    return False


def needs_upgrade_to_argon2(stored_hash: str) -> bool:
    return detect_hash_kind(stored_hash) == "bcrypt"
