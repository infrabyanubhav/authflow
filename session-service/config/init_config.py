"""
==============================================================================
AuthFlow Supabase - Session Service Configuration Module
==============================================================================
This module initializes and manages all configuration settings for the session
service. It loads environment variables, sets up logging, and defines service
configurations for Redis, authentication, and API routing.
==============================================================================
"""

import logging
from config.setup_environment import setup_environment
import os       

# =============================================================================
# Logging Configuration
# =============================================================================
# Configure logging for the session service with file output and structured format
logging.basicConfig(
    filename="session-service.log",  # Log file name for session service logs
    level=logging.INFO,              # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format with timestamp
)

# Create logger instance for this module
logger = logging.getLogger(__name__)

# =============================================================================
# Environment Setup
# =============================================================================
# Set the environment and load corresponding configuration
env = "development"  # Environment mode (development/production/test)
setup_environment(env)  # Load environment-specific configuration

# =============================================================================
# Excluded Paths Configuration
# =============================================================================
# Define paths that should be excluded from session verification
# These are typically static routes, documentation, and health checks
excluded_paths = [
    "/docs",        # API documentation endpoint
    "/redoc",       # Alternative API documentation
    "/openapi.json", # OpenAPI specification
    "/health",      # Health check endpoint
    "/health/",     # Health check endpoint (with trailing slash)
    "/auth",        # Authentication endpoint
    "/",            # Root endpoint
    "/verified"     # Verification endpoint
]

# =============================================================================
# Server Configuration
# =============================================================================
# FastAPI server configuration settings
server_config = {
    "host": "0.0.0.0",        # Bind to all available network interfaces
    "port": 8000,              # Server port number
    "summary": "Session Service, Authflow",  # Service summary for API docs
    "description": "Session Service",         # Service description
    "version": "0.1.0",        # API version
    "docs_url": "/docs",       # Swagger UI documentation URL
    "redoc_url": "/redoc",     # ReDoc documentation URL
    "openapi_url": "/openapi.json",  # OpenAPI specification URL
    "title": "Session Service",      # API title
    "description": "Session Service", # API description (duplicate for clarity)
    "version": "0.1.0",        # API version (duplicate for clarity)
    "contact": {               # Contact information for API documentation
        "name": "InfraByAnubhav",     # Developer/team name
        "url": "",                    # Developer website URL
        "email": "infrabyanubhav@gmail.com",  # Contact email
    },
}

# =============================================================================
# Redis Configuration
# =============================================================================
# Redis connection settings for session storage and caching
redis_config = {
    "host": os.getenv("REDIS_HOST") or "localhost",  # Redis server host
    "port": os.getenv("PORT"),                        # Redis server port
    "db": 0,                                          # Redis database number
}

# =============================================================================
# Authentication Configuration
# =============================================================================
# Settings for communicating with the authentication service
auth_config = {
    "auth_url": os.getenv("AUTH_URL")  # URL of the auth service for verification
}

# =============================================================================
# Backend Configuration
# =============================================================================
# Backend service communication settings
backend_config = {
    "backend_url": os.getenv("BACKEND_URL")  # Backend service URL
}

# =============================================================================
# API Prefix Configuration
# =============================================================================
# API routing prefix settings
prefix_config = {
    "prefix": os.getenv("PREFIX")  # API prefix for all endpoints
}