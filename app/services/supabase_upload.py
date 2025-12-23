from . import _mime
from ..core.supabase_clients import supabase_admin
from ..core import config

def supabase_upload_bytes_and_get_url(data: bytes, user_id: str, message_id: str) -> str:
    content_type, ext = _mime._guess_mime_ext(data)
    key = f"line-images/{user_id}/{message_id}{ext}"

    supabase_admin.storage.from_(config.SUPABASE_BUCKET).upload(
        path=key,
        file=data,
        file_options={"content-type": content_type, "upsert": "true"},
    )

    try:
        public_url = supabase_admin.storage.from_(config.SUPABASE_BUCKET).get_public_url(key)
        if public_url and isinstance(public_url, str) and public_url.startswith("http"):
            return public_url
    except Exception:
        pass

    signed = supabase_admin.storage.from_(config.SUPABASE_BUCKET).create_signed_url(key, 31536000)
    if isinstance(signed, dict):
        return signed.get("signedURL") or signed.get("signed_url")
    return signed
