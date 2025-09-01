"""
==============================================================================
AuthFlow Supabase - Server Initialization Module
==============================================================================
This module initializes and configures the FastAPI application for the AuthFlow
authentication service. It sets up middleware, routes, static files, and all
necessary components for handling authentication requests.

Key Features:
- FastAPI application setup
- Middleware configuration (CORS, Sessions)
- Route registration and prefixing
- Static file serving
- Security configurations
- Logging and monitoring

Author: AuthFlow Team
Version: 0.1.0
==============================================================================
"""

import os
from datetime import datetime

import tabulate as tb
from api.v1.routes.health.__int__ import router as health_router
from api.v1.routes.simple_auth import router as simple_auth_router
from api.v1.routes.welcome import router as welcome_router
from config.init_config import api_config, secrets_config, server_config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from key_store.generate_secrets import generate_key
from service.logs.logger import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# =============================================================================
# Server Initialization
# =============================================================================
# This file is used to initialize the server
# The project is built with FastAPI and Starlette,
# app: FastAPI is the main application object
# config: init_config.py is the configuration file
# api: v1/routes: simple_auth.py is the router for the simple auth routes
# api: v1/routes: welcome.py is the router for the welcome routes
# key_store: generate_secrets.py is the file that generates the secrets for the application
# service: logs: logger.py is the file that logs the application

print("Loading server config from path", " /config/init_config.py")

# =============================================================================
# FastAPI Application Creation
# =============================================================================
# Create FastAPI application with configuration from server_config
# This includes title, description, version, and contact information
app = FastAPI(**server_config)

# =============================================================================
# Security Key Generation
# =============================================================================
# Generate encryption keys for session management and security
# This creates the key_store/key.txt file if it doesn't exist
generate_key()

# =============================================================================
# Middleware Configuration
# =============================================================================
# Add session middleware for OAuth state management and static files
# This enables session-based authentication and state management
app.add_middleware(SessionMiddleware, secret_key=secrets_config["session_secret_key"])

# =============================================================================
# CORS Configuration
# =============================================================================
# Configure Cross-Origin Resource Sharing (CORS) for web applications
# This allows the frontend to communicate with the API from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://session-service:8000", "*"],  # Allow all origins in development
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# =============================================================================
# Static File Serving
# =============================================================================
# Mount static files directory for serving CSS, JS, images, etc.
# This makes static files available at /static/ URL path
app.mount("/static", StaticFiles(directory="static"), name="static")

# =============================================================================
# Route Registration
# =============================================================================
# Register API routes with appropriate prefixes and configurations

# Authentication routes with API version prefix
# Routes: /api/v1/simple_auth/* (signup, signin, logout, password reset)
app.include_router(simple_auth_router, prefix=api_config["prefix"] + "/simple_auth")

# Welcome/success routes for authentication flow
# Routes: /session-success/* (welcome page after successful authentication)
app.include_router(welcome_router, prefix="/session-success")

# Health check routes (no prefix for easy access)
# Routes: /health (service health monitoring)
app.include_router(health_router)

# =============================================================================
# Route Documentation
# =============================================================================
# Generate a table of all registered routes for debugging and documentation
list_of_routes = []

for route in app.routes:
    list_of_routes.append((route.path, route.name))

# Create a formatted table of all routes
table = tb.tabulate(
    list_of_routes, headers=["Path", "Name"], tablefmt="grid", showindex=True
)

# Print the route table for debugging and documentation
print(table)

# =============================================================================
# Server Startup Logging
# =============================================================================
# Log server startup information for monitoring and debugging
logger.info("--------------------------------")
logger.info(
    "Welcome to AuthFlow Service, A secure and fast auth service for you made by developer for developers"
)
logger.info("--------------------------------")
logger.info(
    "Server was started at port 8000 on 0.0.0.0 at %s by %s",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    os.getlogin(),
)
