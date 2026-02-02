from linebot.models import MessageEvent, TextMessage, TextSendMessage
from ..core.line import line_bot_api, handler
from ..services.gemini import GeminiService

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_message = event.message.text
    # Get reply from Gemini
    reply_text = __import__("asyncio").run(GeminiService.generate_reply(user_message))
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text),
    )
