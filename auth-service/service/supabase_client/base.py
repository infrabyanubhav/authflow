from service.logs.logger import logger
from service.supabase_client.client import get_supabase_client
from supabase import Client


class SupabaseClient:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        logger.info("Supabase client initialized")
