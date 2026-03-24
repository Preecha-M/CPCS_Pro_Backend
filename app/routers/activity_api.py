from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from ..services.audit_log import insert_audit
from ..services.request_meta import extract_request_device_meta

router = APIRouter()


class PageViewBody(BaseModel):
    path: str = Field(..., max_length=512)


@router.post("/activity/page-view")
async def log_page_view(request: Request, body: PageViewBody):
    device_meta = extract_request_device_meta(request)
    insert_audit(
        "page_view",
        {
            "path": body.path[:512],
            "device": device_meta,
        },
    )
    return {"ok": True}
