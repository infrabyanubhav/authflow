"""
==============================================================================
AuthFlow Supabase - Main Application Entry Point
==============================================================================
This is the main entry point for the AuthFlow authentication service.
It initializes the environment, loads configuration, and starts the server.

Key Features:
- Environment setup and configuration loading
- Server initialization and startup
- Error handling and logging
- Production-ready application structure

Author: AuthFlow Team
Version: 0.1.0
==============================================================================
"""

import os

from config.init_config import setup_environment
from server.init_server import app
from server.start_server import start_server

# =============================================================================
# Application Entry Point
# =============================================================================
# This block runs when the script is executed directly
# It sets up the environment and starts the server
if __name__ == "__main__":
    # =============================================================================
    # Environment Setup
    # =============================================================================
    # Initialize the development environment
    # This loads environment variables and sets up configuration
    setup_environment("development")
    
    # =============================================================================
    # Configuration Verification
    # =============================================================================
    # Print database URL for debugging (remove in production)
    # This helps verify that environment variables are loaded correctly
    print(os.getenv("DATABASE_URL"))
    
    # =============================================================================
    # Server Startup
    # =============================================================================
    # Start the FastAPI server with the configured application
    # This begins listening for HTTP requests on the configured port
    start_server(app)
