import os
import requests

def weather_condition_label(code: int):
    table = {
        1: "ฟ้าแจ้ง (Clear)",
        2: "มีเมฆบางส่วน (Partly cloudy)",
        3: "เมฆเป็นส่วนมาก (Cloudy)",
        4: "มีเมฆมาก (Overcast)",
        5: "ฝนเล็กน้อย (Light rain)",
        6: "ฝนปานกลาง (Moderate rain)",
        7: "ฝนหนัก (Heavy rain)",
        8: "พายุฝนฟ้าคะนอง (Thunderstorm)",
        9: "อากาศหนาวจัด (Very cold)",
        10: "อากาศหนาว (Cold)",
        11: "อากาศร้อน (Hot)",
        12: "อากาศร้อนจัด (Very hot)",
    }
    return table.get(code, f"Unknown ({code})")

async def fetch_api_data(date: str, lat: str, lon: str):
    url = "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/at"
    querystring = {
        "lat": lat,
        "lon": lon,
        "fields": "tc,rh,rain,slp,ws10m,wd10m,cloudlow,cloudmed,cloudhigh,cond",
        "date": date,
        "duration": "1",
    }
    headers = {
        "accept": "application/json",
        "Authorization": os.getenv("TMD_BEARER", ""),
    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": str(e)}
