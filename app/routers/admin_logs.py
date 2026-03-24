from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..core.auth import get_current_user_from_cookie
from ..core.mongo import col_audit_logs, DESCENDING

router = APIRouter()

_ALLOWED_KINDS = frozenset(
    {"access", "security", "system_error", "page_view", "rejected_rice_image", "all"}
)


def _serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(doc)
    oid = out.pop("_id", None)
    out["id"] = str(oid) if oid is not None else None
    ca = out.get("created_at")
    if isinstance(ca, datetime):
        out["created_at"] = ca.isoformat()
    return out


@router.get("/admin/logs")
async def list_audit_logs(
    request: Request,
    kind: str = "all",
    page: int = 1,
    limit: int = 50,
):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    k = (kind or "all").strip()
    if k not in _ALLOWED_KINDS:
        return JSONResponse({"detail": "Invalid kind"}, status_code=400)

    page = max(1, page)
    limit = min(max(1, limit), 200)
    skip = (page - 1) * limit

    query: Dict[str, Any] = {}
    if k != "all":
        query["kind"] = k

    total = col_audit_logs.count_documents(query)
    cursor = (
        col_audit_logs.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
    )
    items: List[Dict[str, Any]] = [_serialize_doc(d) for d in cursor]

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if total else 0,
        "kind": k,
    }


@router.get("/admin/logs/{log_id}")
async def get_audit_log(log_id: str, request: Request):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    try:
        oid = ObjectId(log_id)
    except Exception:
        return JSONResponse({"detail": "Not found"}, status_code=404)

    doc = col_audit_logs.find_one({"_id": oid})
    if not doc:
        return JSONResponse({"detail": "Not found"}, status_code=404)

    return {"item": _serialize_doc(doc)}
