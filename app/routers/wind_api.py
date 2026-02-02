from fastapi import APIRouter
from datetime import datetime
import requests, math

router = APIRouter(prefix="/api/wind", tags=["wind"])

@router.get("/vector")
def wind_vector(
    lat: float,
    lon: float,
    start: str,  # 2026-01-25T06:00
    end: str     # 2026-01-25T18:00
):
    start_date = start.split("T")[0]
    end_date = end.split("T")[0]

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "windspeed_10m,winddirection_10m",
        "timezone": "Asia/Bangkok"
    }

    r = requests.get(url, params=params).json()

    data = []
    for t, spd, deg in zip(
        r["hourly"]["time"],
        r["hourly"]["windspeed_10m"],
        r["hourly"]["winddirection_10m"]
    ):
        if start <= t <= end:
            rad = math.radians(deg)
            data.append({
                "time": t,
                "u": spd * math.sin(rad),
                "v": spd * math.cos(rad),
                "speed": spd,
                "direction": deg
            })

    return {"data": data}
