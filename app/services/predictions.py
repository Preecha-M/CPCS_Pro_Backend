import re
from datetime import datetime
from ..core.mongo import col_predictions, DESCENDING
from ..core.line import line_bot_api

def parse_prediction(pred_text: str):
    if not pred_text:
        return None, None

    disease = None
    disease = None
    # Use generic search instead of first line dependent
    # Support both "ผลการทำนาย" and "ผลการวินิจฉัย"
    m = re.search(r"(?:ผลการทำนาย|ผลการวินิจฉัย):\s*([^\n]+)", pred_text)
    if m:
        disease = m.group(1).strip()

    conf = None
    m2 = re.search(r"ความมั่นใจ:\s*([0-9]*\.?[0-9]+)", pred_text)
    if m2:
        try:
            conf = float(m2.group(1))
        except Exception:
            conf = None

    return disease, conf

def save_direct_to_userdata(user_id, image_url, result, dedup_key: str):
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name

    disease_name, conf = parse_prediction(result)

    now_iso = datetime.now().isoformat()
    today = datetime.now().strftime("%Y-%m-%d")

    col_predictions.update_one(
        {"_dedup": dedup_key},
        {
            "$setOnInsert": {
                "_dedup": dedup_key,
                "user_id": user_id,
                "display_name": display_name,
                "image_url": image_url,
                "prediction": result,
                "timestamp": now_iso,
                "address": "ไม่ระบุ",
                "latitude": None,
                "longitude": None,
                "disease": disease_name,
                "confidence": conf,
                "date": today,
            }
        },
        upsert=True,
    )

def update_location_in_userdata(user_id, latitude, longitude, address):
    last_doc = col_predictions.find_one({"user_id": user_id}, sort=[("timestamp", DESCENDING)])
    if not last_doc:
        return
    col_predictions.update_one(
        {"_id": last_doc["_id"]},
        {"$set": {"latitude": float(latitude), "longitude": float(longitude), "address": address}},
    )
