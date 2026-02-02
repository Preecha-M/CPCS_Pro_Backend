from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from ..core.auth import get_current_user_from_cookie
from ..core.mongo import col_predictions
from ..services.weather import fetch_api_data, weather_condition_label

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

    # Extract location and timestamp for weather data
    latitude = record.get("latitude")
    longitude = record.get("longitude")
    timestamp_str = record.get("timestamp", "")

    # Parse date from timestamp for weather API
    # Assuming timestamp format like "2024-01-31 14:30:00"
    weather_data = None
    weather_list = []

    if latitude and longitude and timestamp_str:
        try:
            # Extract date from timestamp
            if isinstance(timestamp_str, str):
                date_part = timestamp_str.split()[0]  # Get YYYY-MM-DD part
            else:
                date_part = datetime.now().strftime("%Y-%m-%d")

            # Fetch weather data for the record's location and date
            api_data = await fetch_api_data(
                date_part, str(latitude), str(longitude)
            )

            if isinstance(api_data, dict) and "error" not in api_data:
                weather_data = api_data

                # Build weather list with wind data
                forecasts = api_data.get("WeatherForecasts", {}).get("forecasts", [])
                for forecast in forecasts:
                    time = forecast.get("time", "")
                    items = []

                    # Extract all weather parameters including wind data
                    for key in ["tc", "rh", "rain", "slp", "ws10m", "wd10m", "cloudlow", "cloudmed", "cloudhigh", "cond"]:
                        if key in forecast:
                            value = forecast.get(key)
                            if key == "cond":
                                try:
                                    value = weather_condition_label(int(value))
                                except Exception:
                                    pass
                            items.append({"label": key, "value": str(value)})

                    weather_list.append({
                        "time": time,
                        "data": items,
                        "ws10m": forecast.get("ws10m"),  # Wind speed
                        "wd10m": forecast.get("wd10m"),  # Wind direction
                    })

        except Exception as e:
            print(f"Error fetching weather data: {e}")

    return {
        "record": record,
        "weather_data": weather_data,
        "weather_list": weather_list,
    }
