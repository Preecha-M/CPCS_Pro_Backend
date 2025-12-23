from datetime import datetime
from ..core.mongo import col_temp_locations

def save_temp_location(user_id, latitude, longitude, address):
    col_temp_locations.insert_one(
        {
            "user_id": user_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "address": address,
            "timestamp": datetime.now().isoformat(),
        }
    )
