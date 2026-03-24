import certifi
from pymongo import MongoClient, ASCENDING, DESCENDING
from . import config

mongo_client = MongoClient(config.MONGODB_URI, tlsCAFile=certifi.where())
db = mongo_client[config.MONGODB_DB]

# Collections
col_users = db["users"]
col_predictions = db["predictions"]
col_temp_locations = db["temp_locations"]
col_audit_logs = db["audit_logs"]

# Indexes (same as original)
col_predictions.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
col_predictions.create_index([("latitude", ASCENDING), ("longitude", ASCENDING)])
col_temp_locations.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
col_audit_logs.create_index([("created_at", DESCENDING)])
col_audit_logs.create_index([("kind", ASCENDING), ("created_at", DESCENDING)])

__all__ = [
    "ASCENDING",
    "DESCENDING",
    "mongo_client",
    "db",
    "col_users",
    "col_predictions",
    "col_temp_locations",
    "col_audit_logs",
]
