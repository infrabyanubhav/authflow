"""
AuthFlow Supabase - Configuration Management Module

This module centralizes all configuration settings for the AuthFlow service,
including API, database, Redis, Supabase, and security configurations.

Environment variables are loaded with sensible defaults for development.
Production deployments should override these with proper environment variables.

Author: AuthFlow Team
Version: 0.1.0
"""

import os

import dotenv
from config.load_environment import setup_environment

# Set environment and load configuration
env = "development"  # Default to development environment
setup_environment(env)  # Load environment-specific settings

# =============================================================================
# API Configuration
# =============================================================================
api_config = {
    "prefix": os.getenv("API_PREFIX") or "/api/v1",  # API version prefix
    "verify_url": os.getenv("VERIFY_URL") or "/verify-service/session",  # Verify URL
}

# =============================================================================
# Database Configuration
# =============================================================================
db_config = {
    "url": os.getenv("DATABASE_URL")  # PostgreSQL connection string
}

# =============================================================================
# Redis Configuration
# =============================================================================
redis_config = {
    "host": os.getenv("REDIS_HOST"),  # Redis server hostname/IP
    "port": int(os.getenv("REDIS_PORT") or 6379),  # Redis server port
    "password": os.getenv("REDIS_PASSWORD"),  # Redis authentication password
    "db": int(os.getenv("REDIS_DB") or 0),  # Redis database number
    "ttl": int(os.getenv("REDIS_TTL") or 3600),  # Session TTL in seconds (1 hour)
}

# =============================================================================
# Security & Secrets Configuration
# =============================================================================
secrets_config = {
    "session_secret_key": os.getenv("SESSION_SECRET_KEY")  # Secret key for session encryption
}

# =============================================================================
# Server Configuration
# =============================================================================
server_config = {
    "host": "0.0.0.0",  # Bind to all network interfaces
    "port": 8001,  # Server port number
    "summary": "Auth Service for Eorix",  # Service summary for API docs
    "description": "Auth Service for Eorix",  # Service description
    "version": "0.1.0",  # Service version
    "docs_url": "/docs",  # Swagger UI documentation endpoint
    "redoc_url": "/redoc",  # ReDoc documentation endpoint
    "openapi_url": "/openapi.json",  # OpenAPI specification endpoint
    "title": "Auth Service",  # Service title
    "contact": {
        "name": "Eorix",  # Organization name
        "url": "https://eorix.io",  # Organization website
        "email": "contact@eorix.io",  # Contact email
    },
}

# =============================================================================
# Supabase Configuration
# =============================================================================
supabase_config = {
    "url": os.getenv("SUPABASE_URL"),  # Supabase project URL
    "key": os.getenv("SUPABASE_KEY"),  # Supabase API key
    "reset_password_redirect_to": os.getenv("RESET_PASSWORD_REDIRECT_TO"),  # Password reset redirect URL
    "email_verification_redirect_to": os.getenv("EMAIL_VERIFICATION_REDIRECT_TO"),  # Email verification redirect URL
}

# =============================================================================
# URL Routing & Proxy Configuration
# =============================================================================
allowed_urls = {
    "session_service": ["http://session-service:8000/verify/"],  # Session service verification endpoint
    "allowed_proxy": ["http://session-service:8000"],  # Allowed proxy services
}

forward_urls = {
    "session_service": ["http://session-service:8000/verify"],  # URLs to forward to session service
}

# =============================================================================
# Security & Access Control
# =============================================================================
unsecure_urls = [
    "/docs",  # API documentation (public access)
    "/redoc",  # Alternative API docs (public access)
    "/openapi.json",  # OpenAPI spec (public access)
    "/health",  # Health check endpoint (public access)
    "/health/",  # Health check endpoint with trailing slash
    "/auth",  # Authentication endpoints (public access)
]

# =============================================================================
# Template & UI Configuration
# =============================================================================
template_path = "templates"  # Path to HTML template files

# =============================================================================
# Cookie Configuration
# =============================================================================
cookie_config = {
    "cookie_name": os.getenv("COOKIE_NAME") or "session_id",  # Session cookie name
    "cookie_domain": os.getenv("COOKIE_DOMAIN") or "localhost",  # Cookie domain
    "cookie_path": os.getenv("COOKIE_PATH") or "/",  # Cookie path
    "cookie_max_age": int(os.getenv("COOKIE_MAX_AGE") or 3600),  # Cookie expiration in seconds
    "cookie_secure": os.getenv("COOKIE_SECURE") or False,  # HTTPS-only cookies (production: True)
    "cookie_samesite": os.getenv("COOKIE_SAMESITE") or "Lax",  # SameSite cookie policy
    "cookie_httponly": os.getenv("COOKIE_HTTPONLY") or True,  # HTTP-only cookies (security)
}

# =============================================================================
# Logging Configuration
# =============================================================================
log_settings = {
    "log_level": os.getenv("LOG_LEVEL") or "INFO",  # Logging level (DEBUG, INFO, WARNING, ERROR)
    "log_file": os.getenv("LOG_FILE") or "auth-service.log",  # Log file path
}

# =============================================================================
# Testing Configuration
# =============================================================================
test_db_config = {
    "url": "sqlite:///./test.db"  # SQLite database for testing (in-memory option available)
}

# =============================================================================
# Service Startup Message
# =============================================================================
print("--------------------------------")
print(
    "Welcome to AuthFlow Service, A secure and fast auth service for you made by developer for developers"
)
print("--------------------------------")
