from linebot import LineBotApi, WebhookHandler
from . import config

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

__all__ = ["line_bot_api", "handler"]
