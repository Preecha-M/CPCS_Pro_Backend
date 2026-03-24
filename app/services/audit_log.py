from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..core.mongo import col_audit_logs


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def insert_audit(kind: str, payload: Dict[str, Any]) -> Optional[str]:
    doc = {"kind": kind, "created_at": utcnow(), "payload": payload}
    res = col_audit_logs.insert_one(doc)
    return str(res.inserted_id)
