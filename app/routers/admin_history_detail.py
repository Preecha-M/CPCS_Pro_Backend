from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from ..core.auth import get_current_user_from_cookie
from ..core.mongo import col_predictions


router = APIRouter()


@router.get("/admin/history/{record_id}")
async def get_history_detail(record_id: str, request: Request):
    """
    Get detailed information for a specific history record including weather data.
    """
    payload = get_current_user_from_cookie(request)
    if payload.get("role") not in ("admin", "researcher"):
        return JSONResponse({"detail": "Forbidden"}, status_code=403)

    # Try to find record by ObjectId first, then by other fields
    try:
        record = col_predictions.find_one({"_id": ObjectId(record_id)})
    except Exception:
        # If not a valid ObjectId, try finding by timestamp or other unique identifier
        record = None

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Convert ObjectId to string for JSON serialization
    if "_id" in record:
        record["id"] = str(record["_id"])
        del record["_id"]



    return {
        "record": record,
        "record": record,
    }
