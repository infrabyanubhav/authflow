"""
==============================================================================
AuthFlow Supabase - Session Service Server Startup Module
==============================================================================
This module handles the startup and configuration of the FastAPI server
for the session service. It uses uvicorn as the ASGI server to run the
FastAPI application with proper host and port configuration.
==============================================================================
"""

import uvicorn
from config.init_config import logger
from fastapi import FastAPI

def start_server(app: FastAPI):
    """
    Start the FastAPI server for the session service.
    
    This function initializes and starts the uvicorn ASGI server with the
    configured FastAPI application. The server runs on all network interfaces
    (0.0.0.0) on port 8000.
    
    Args:
        app (FastAPI): FastAPI application instance to be served
    
    Server Configuration:
        - Host: 0.0.0.0 (bind to all available network interfaces)
        - Port: 8000 (default session service port)
        - Reload: False (disable auto-reload for production stability)
    
    Note:
        - The server runs in production mode with reload disabled
        - All network interfaces are bound for container deployment
        - Port 8000 is the standard port for the session service
    """
    # =============================================================================
    # Server Startup Logging
    # =============================================================================
    # Log the server startup process
    logger.info("Starting session service server")
    
    # =============================================================================
    # Uvicorn Server Configuration
    # =============================================================================
    # Start the uvicorn ASGI server with the FastAPI application
    uvicorn.run(
        app,                    # FastAPI application instance
        host="0.0.0.0",        # Bind to all network interfaces
        port=8000,             # Session service port
        reload=False           # Disable auto-reload for production
    )
