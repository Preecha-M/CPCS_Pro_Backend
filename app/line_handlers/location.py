from linebot.models import MessageEvent, LocationMessage, TextSendMessage

from ..core.line import line_bot_api, handler
from ..state import user_pending_location_request
from ..services.temp_locations import save_temp_location
from ..services.predictions import update_location_in_userdata
from ._expiry import remove_expired_requests

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    user_id = event.source.user_id

    remove_expired_requests()

    if user_id not in user_pending_location_request:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("กรุณาส่งรูปก่อน แล้วค่อยส่ง Location เพื่อผูกกับรูปครับ"),
        )
        return

    latitude = event.message.latitude
    longitude = event.message.longitude
    address = event.message.address

    save_temp_location(user_id, latitude, longitude, address)
    update_location_in_userdata(user_id, latitude, longitude, address)

    user_pending_location_request.pop(user_id, None)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=(
                f"✅ ได้รับตำแหน่งแล้ว!\n📍 {address}\n"
                f"ละติจูด: {latitude}\nลองจิจูด: {longitude}\n"
                "ระบบผูกพิกัดกับรูปล่าสุดเรียบร้อยแล้วครับ ✅"
            )
        ),
    )
