from linebot.models import MessageEvent, TextMessage, TextSendMessage
from ..core.line import line_bot_api, handler

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="ระบบรองรับการวิเคราะห์จากรูปใบข้าวเท่านั้น กรุณาส่งรูปใบข้าวเพื่อจำแนกโรคครับ"),
    )
