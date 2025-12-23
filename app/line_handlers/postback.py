import json
from linebot.models import PostbackEvent, TextSendMessage

from ..core.line import line_bot_api, handler
from ..core.mongo import col_predictions, DESCENDING

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    try:
        selected_data = json.loads(event.postback.data)
    except Exception:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="รูปแบบข้อมูลไม่ถูกต้อง"))
        return

    latitude = selected_data.get("latitude")
    longitude = selected_data.get("longitude")
    address = selected_data.get("address") or "ไม่ระบุสถานที่"

    last_doc = col_predictions.find_one({"user_id": user_id}, sort=[("timestamp", DESCENDING)])
    if not last_doc:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ ไม่พบรายการรูปของคุณ"))
        return

    col_predictions.update_one(
        {"_id": last_doc["_id"]},
        {
            "$set": {
                "latitude": float(latitude) if latitude is not None else None,
                "longitude": float(longitude) if longitude is not None else None,
                "address": address,
            }
        },
    )

    display_name = last_doc.get("display_name", "")
    pred_text = last_doc.get("prediction", "")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=f"✅ ผูกพิกัดเรียบร้อย!\n👤 {display_name}\n📍 {address}\n\n🔍 ผลทำนายล่าสุด:\n{pred_text}"
        ),
    )
