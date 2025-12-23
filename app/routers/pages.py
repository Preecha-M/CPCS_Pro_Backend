from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime

from ..core.templates import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def show_index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "current_year": datetime.now().year},
    )

@router.get("/guide", response_class=HTMLResponse)
async def get_guide_page(request: Request):
    return templates.TemplateResponse("guide.html", {"request": request})
