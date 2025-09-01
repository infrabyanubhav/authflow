"""
==============================================================================
AuthFlow Supabase - Session Service Server Initialization Module
==============================================================================
This module configures and initializes the FastAPI application instance for the
session service. It sets up middleware, routes, and all necessary components
for handling session management and authentication with device verification
capabilities.

Components:
    - FastAPI application instance with server configuration
    - Device information verification middleware for security
    - Session management routes under /session prefix
    - Authentication routes under /auth prefix
    - Health check routes under /health prefix
    - CORS middleware for cross-origin requests
==============================================================================
"""

import logging
import tabulate as tb
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes.auth import router as auth_router
from api.v1.routes.health import router as health_router
from api.v1.routes.session import router as session_router
from config.init_config import server_config, prefix_config
from fastapi import FastAPI
from middleware.VerifyDeviceInforMiddleware import VerifyDeviceInfoMiddleware

# =============================================================================
# Logger Configuration
# =============================================================================
# Create logger instance for this module
logger = logging.getLogger(__name__)

# =============================================================================
# FastAPI Application Initialization
# =============================================================================
# Initialize FastAPI application with server configuration from config
app = FastAPI(**server_config)

# =============================================================================
# Middleware Configuration
# =============================================================================
# Add CORS middleware for handling cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://auth-service:8001", "*"],  # Allowed origins
    allow_credentials=True,    # Allow credentials (cookies, authorization headers)
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)

# Add custom device verification middleware for security
app.add_middleware(VerifyDeviceInfoMiddleware)

# =============================================================================
# Route Registration
# =============================================================================
# Register session management routes with API prefix
app.include_router(session_router, prefix=prefix_config.get("prefix") + "/session")
# Register authentication routes with API prefix
app.include_router(auth_router, prefix=prefix_config.get("prefix") + "/auth")
# Register health check routes with API prefix
app.include_router(health_router, prefix=prefix_config.get("prefix") + "/health")

# =============================================================================
# Root Endpoint
# =============================================================================
# Welcome endpoint for the session service
@app.get("/")
def session_service():
    """
    Root endpoint that returns a welcome message for the session service.
    This endpoint is accessible without authentication.
    """
    return {
        "Welcome to Session Service"
    }

# =============================================================================
# Route Documentation
# =============================================================================
# Generate and print a table of all registered routes for debugging
list_of_routes = []
for route in app.routes:
    list_of_routes.append((route.path, route.name))

# Create a formatted table of all routes
table = tb.tabulate(
    list_of_routes, 
    headers=["Path", "Name"], 
    tablefmt="grid", 
    showindex=True
)

# Print the route table for development/debugging purposes
print(table)

# =============================================================================
# Initialization Complete
# =============================================================================
# Log successful initialization
logger.info("FastAPI application initialized successfully")
