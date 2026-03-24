import re
import time
from typing import List, Optional, Tuple

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..core.auth import COOKIE_NAME
from ..services.audit_log import insert_audit
from ..services.request_meta import extract_request_device_meta


def _username_hint(request: Request) -> Optional[str]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
        return payload.get("username")
    except Exception:
        return None


def _should_skip_access_log(request: Request) -> bool:
    path = request.url.path
    if path in ("/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"):
        return True
    if path.startswith("/static/") or path.startswith("/guide_images/"):
        return True
    # มี audit แยก kind page_view แล้ว — ไม่ต้องซ้ำเป็น access
    if path == "/api/activity/page-view" and request.method == "POST":
        return True
    return False


_SECURITY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("script_or_markup", re.compile(r"<script|</script|javascript:|onerror\s*=|onload\s*=|<iframe|data:text/html", re.I)),
    ("path_traversal", re.compile(r"\.\./|\.\.\\|%2e%2e|%252e|%c0%ae", re.I)),
    ("sql_probe", re.compile(r"union\s+select|;\s*drop\s+|'\s*or\s+1\s*=|sleep\s*\(|benchmark\s*\(", re.I)),
    ("cmd_probe", re.compile(r"\|\s*sh\b|`[^`]+`|;\s*(wget|curl)\b", re.I)),
]


def _security_flags(method: str, path: str, query: str, ua: str) -> List[str]:
    hay = f"{method} {path}?{query} {ua}"
    flags: List[str] = []
    for name, pat in _SECURITY_PATTERNS:
        if pat.search(hay):
            flags.append(name)
    if len(query) > 1500:
        flags.append("long_query_string")
    return flags


class AccessAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            try:
                path = request.url.path
                query = request.url.query or ""
                device_meta = extract_request_device_meta(request)
                ua = (device_meta.get("user_agent") or "")[:500]
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                status = getattr(response, "status_code", 0) if response is not None else 0

                flags = _security_flags(request.method, path, query, ua)
                if flags:
                    insert_audit(
                        "security",
                        {
                            "method": request.method,
                            "path": path[:1024],
                            "query": query[:2048],
                            "flags": flags,
                            "status_code": status,
                            "username_hint": _username_hint(request),
                            "device": device_meta,
                        },
                    )

                if not _should_skip_access_log(request):
                    insert_audit(
                        "access",
                        {
                            "method": request.method,
                            "path": path[:1024],
                            "query": query[:2048],
                            "status_code": status,
                            "duration_ms": duration_ms,
                            "username_hint": _username_hint(request),
                            "security_flags": flags,
                            "device": device_meta,
                        },
                    )
            except Exception:
                pass
