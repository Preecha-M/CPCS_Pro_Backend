from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from ..services.audit_log import insert_audit

router = APIRouter()


class PageViewBody(BaseModel):
    path: str = Field(..., max_length=512)


@router.post("/activity/page-view")
async def log_page_view(request: Request, body: PageViewBody):
    insert_audit(
        "page_view",
        {
            "path": body.path[:512],
            "referer": (request.headers.get("referer") or "")[:512],
            "ip": request.client.host if request.client else None,
            "user_agent": (request.headers.get("user-agent") or "")[:400],
        },
    )
    return {"ok": True}
