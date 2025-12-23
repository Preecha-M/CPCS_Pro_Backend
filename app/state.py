from .core import config

# State / Config (same as original)
EXPIRY_MINUTES = config.EXPIRY_MINUTES
user_pending_location_request = {}

__all__ = ["EXPIRY_MINUTES", "user_pending_location_request"]
