from .core import config

# State / Config (same as original)
# State / Config (same as original)
EXPIRY_MINUTES = config.EXPIRY_MINUTES
user_pending_location_request = {}

# Gemini State
CURRENT_GEMINI_MODEL = config.GEMINI_MODEL_PRIMARY
GEMINI_QUOTA_RESET_TIME = None

__all__ = ["EXPIRY_MINUTES", "user_pending_location_request", "CURRENT_GEMINI_MODEL", "GEMINI_QUOTA_RESET_TIME"]
