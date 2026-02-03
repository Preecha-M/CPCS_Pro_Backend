import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "riceapp")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "rice-images")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

HF_SPACE = os.getenv("HF_SPACE", "Teayear/Rice_EfficientNetB1")
CLIP_THRESHOLD = float(os.getenv("CLIP_THRESHOLD", "0.45"))

EXPIRY_MINUTES = int(os.getenv("EXPIRY_MINUTES", "10"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_PRIMARY = os.getenv("GEMINI_MODEL_PRIMARY", "gemini-3-flash-preview")
GEMINI_MODEL_FALLBACK = os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash")

