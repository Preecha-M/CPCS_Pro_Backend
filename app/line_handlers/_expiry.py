from datetime import datetime, timedelta
from ..state import EXPIRY_MINUTES, user_pending_location_request

def remove_expired_requests():
    now = datetime.now()
    expired = []
    for user_id, data in user_pending_location_request.items():
        try:
            ts = datetime.fromisoformat(data["timestamp"])
            if now - ts > timedelta(minutes=EXPIRY_MINUTES):
                expired.append(user_id)
        except Exception:
            expired.append(user_id)
    for uid in expired:
        user_pending_location_request.pop(uid, None)
