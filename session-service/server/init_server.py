"""
FastAPI Server Initialization Module

This module configures and initializes the FastAPI application instance for the session service.
It sets up middleware, routes, and all necessary components for handling session management
and authentication with device verification capabilities.

Components:
    - FastAPI application instance with server configuration
    - Device information verification middleware for security
    - Session management routes under /app prefix
    - Authentication routes under /auth prefix
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

logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(**server_config)

# Add middleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001/", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.add_middleware(VerifyDeviceInfoMiddleware)
app.include_router(session_router, prefix=prefix_config.get("prefix") + "/session")
app.include_router(auth_router, prefix=prefix_config.get("prefix") + "/auth")
app.include_router(health_router, prefix=prefix_config.get("prefix") + "/health")


@app.get("/")
def session_service():
      return {
         "Welcome to Session Service"
      }
   

    


# Print all routes
list_of_routes = []
for route in app.routes:

    list_of_routes.append((route.path, route.name))

table = tb.tabulate(
    list_of_routes, headers=["Path", "Name"], tablefmt="grid", showindex=True
)

print(table)


logger.info("FastAPI application initialized successfully")
