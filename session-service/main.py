"""
==============================================================================
AuthFlow Supabase - Session Service Main Entry Point
==============================================================================
This is the main entry point for the AuthFlow session service.
It initializes the environment, loads configuration, and starts the server.
The session service handles user session management, device tracking,
and session validation for the AuthFlow authentication system.
==============================================================================
"""

from server.start_server import start_server
from server.init_server import app
from config.setup_environment import setup_environment

# =============================================================================
# Application Startup
# =============================================================================
if __name__ == "__main__":
    # =============================================================================
    # Environment Initialization
    # =============================================================================
    # Load environment-specific configuration (development/production)
    setup_environment("development")
    
    # =============================================================================
    # Server Startup
    # =============================================================================
    # Start the FastAPI server with the configured application
    start_server(app)
