import os
import tempfile

from linebot.models import MessageEvent, ImageMessage, TextSendMessage

from ..core.line import line_bot_api, handler
from ..core.gradio_space import gr_client, handle_file
from ..core import config
from ..services.supabase_upload import (
    supabase_upload_bytes_and_get_url,
    supabase_upload_rejected_rice_image,
)
from ..services.predictions import save_direct_to_userdata
from ..services.audit_log import insert_audit
from ..state import user_pending_location_request

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id

    message_content = line_bot_api.get_message_content(event.message.id)
    img_bytes = b"".join(chunk for chunk in message_content.iter_content())

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_pred:
        tmp_pred.write(img_bytes)
        tmp_pred_path = tmp_pred.name

    try:
        # Space รับ 2 input: image + clip_threshold
        result = gr_client.predict(
            handle_file(tmp_pred_path),
            float(config.CLIP_THRESHOLD),
            api_name="/predict",
        )
    except Exception as e:
        try:
            insert_audit(
                "system_error",
                {
                    "source": "line_image_predict",
                    "user_id": user_id,
                    "message": str(e)[:2000],
                },
            )
        except Exception:
            pass
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ ระบบทำนายขัดข้องชั่วคราว กรุณาลองใหม่\nรายละเอียด: {e}"),
        )
        return
    finally:
        try:
            os.remove(tmp_pred_path)
        except Exception:
            pass

    # ✅ ให้ Space เป็นคน gate: ถ้าไม่ใช่ใบข้าว -> ตีกลับและไม่บันทึก/ไม่ขอพิกัด
    if isinstance(result, str) and "ไม่ใช่รูปใบข้าว" in result:
        image_url = None
        upload_error = None
        try:
            image_url = supabase_upload_rejected_rice_image(
                img_bytes, user_id, event.message.id
            )
        except Exception as up_e:
            upload_error = str(up_e)[:500]
        try:
            insert_audit(
                "rejected_rice_image",
                {
                    "user_id": user_id,
                    "line_message_id": event.message.id,
                    "image_url": image_url,
                    "upload_error": upload_error,
                    "model_reply": result[:2000],
                    "clip_threshold": float(config.CLIP_THRESHOLD),
                },
            )
        except Exception:
            pass
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    try:
        image_url = supabase_upload_bytes_and_get_url(img_bytes, user_id, event.message.id)
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ อัปโหลดรูปไม่สำเร็จ กรุณาลองใหม่\nรายละเอียด: {e}"),
        )
        return

    dedup_key = f"{user_id}:{event.message.id}"
    save_direct_to_userdata(user_id, image_url, result, dedup_key)

    user_pending_location_request[user_id] = {"timestamp": __import__("datetime").datetime.now().isoformat()}

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=(
                "🔍 ผลการวิเคราะห์:\n"
                f"{result}\n\n"
                "📍 กรุณาส่ง Location ใหม่ของแปลงนี้ เพื่อผูกกับรูปนี้ (แชร์พิกัดจากแผนที่)"
            )
        ),
    )
