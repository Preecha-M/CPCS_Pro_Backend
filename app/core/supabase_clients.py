from supabase import create_client, Client as SupabaseClient
from . import config

supabase: SupabaseClient = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
supabase_admin: SupabaseClient = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)

__all__ = ["SupabaseClient", "supabase", "supabase_admin"]
