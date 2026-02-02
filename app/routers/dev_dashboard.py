from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from ..core.auth import get_current_user_from_cookie
from ..core import config
from .. import state
from ..core.mongo import col_users

router = APIRouter()

class ModelUpdate(BaseModel):
    model_name: str

@router.get("/dev/status")
async def get_dev_status(request: Request):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin/Dev only")

    return {
        "current_model": state.CURRENT_GEMINI_MODEL,
        "primary_model": config.GEMINI_MODEL_PRIMARY,
        "fallback_model": config.GEMINI_MODEL_FALLBACK,
        "quota_reset_time": state.GEMINI_QUOTA_RESET_TIME,
        "server_time": datetime.now(),
        "api_key_configured": bool(config.GEMINI_API_KEY)
    }

@router.post("/dev/model")
async def set_dev_model(request: Request, body: ModelUpdate):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin/Dev only")
    
    # Allow switching to any model string, or restrict? 
    # Let's allow flexibility but maybe just basic validation
    if not body.model_name:
         raise HTTPException(status_code=400, detail="Model name required")

    state.CURRENT_GEMINI_MODEL = body.model_name
    # Reset limit timer if we manually switch? Maybe.
    # If user forces switch to Primary, we should probably clear the reset timer.
    if body.model_name == config.GEMINI_MODEL_PRIMARY:
        state.GEMINI_QUOTA_RESET_TIME = None

    return {
        "ok": True, 
        "current_model": state.CURRENT_GEMINI_MODEL,
        "message": f"Switched to {body.model_name}"
    }

@router.get("/dev/users")
async def get_dev_users(request: Request):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin/Dev only")
    
    users = list(col_users.find({}, {"password_hash": 0, "_id": 0}))
    return {
        "count": len(users),
        "users": users
    }
