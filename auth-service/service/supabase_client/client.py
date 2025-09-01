from config.init_config import supabase_config
from dotenv import load_dotenv
from service.logs.logger import logger
from supabase import Client, ClientOptions, create_client

# Lazy load supabase client to avoid import-time initialization issues
_supabase_client: Client = None


def get_supabase_client():
    """Get or create supabase client lazily"""
    global _supabase_client
    if _supabase_client is None:
        load_dotenv()
        url: str = supabase_config.get("url")
        key: str = supabase_config.get("key")

        if url and key:
            logger.info("Creating supabase client")
            _supabase_client = create_client(
                url, key, options=ClientOptions(flow_type="pkce")
            )
        else:
            logger.warning("Supabase URL or key not found in environment")
            _supabase_client = None

    return _supabase_client
