from ..core.line import handler

def handle_events(body: bytes, signature: str):
    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        print(f"Handle error: {e}")
