import os

import dotenv

dotenv.load_dotenv("env/.env.development")


db_config = {"url": os.getenv("DATABASE_URL") or "sqlite:///./db.sqlite3"}


redis_config = {
    "host": os.getenv("REDIS_HOST") or "localhost",
    "port": int(os.getenv("REDIS_PORT") or 6379),
    "password": os.getenv("REDIS_PASSWORD") or "your-secret-key-change-in-production",
    "db": int(os.getenv("REDIS_DB") or 0),
}


secrets_config = {
    "session_secret_key": os.getenv(
        "SESSION_SECRET_KEY" or "your-secret-key-change-in-production"
    )
}


server_config = {
    "host": "0.0.0.0",
    "port": 8001,
    "summary": "Auth Service for Eorix",
    "description": "Auth Service for Eorix",
    "version": "0.1.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
    "title": "Auth Service",
    "description": "Auth Service for Eorix",
    "version": "0.1.0",
    "contact": {
        "name": "Eorix",
        "url": "https://eorix.io",
        "email": "contact@eorix.io",
    },
}


supabase_config = {
    "url": os.getenv("SUPABASE_URL" or "http://localhost:54321"),
    "key": os.getenv("SUPABASE_KEY" or "your-secret-key-change-in-production"),
}

allowed_urls = {
    "session_service": "http://session-service:8000/verify/",
    "allowed_proxy": "http://session-service:8000",
}


forward_urls = {
    "session_service": "http://session-service:8000/verify",
}


unsecure_urls = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/health/",
    "/auth",
]


print("db_config", db_config)
print("redis_config", redis_config)
print("secrets_config", secrets_config)
print("server_config", server_config)
print("supabase_config", supabase_config)
print("allowed_urls", allowed_urls)
print("forward_urls", forward_urls)
print("unsecure_urls", unsecure_urls)
