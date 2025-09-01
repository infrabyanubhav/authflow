"""
==============================================================================
AuthFlow Supabase - Session Service Environment Setup Module
==============================================================================
This module handles the loading of environment-specific configuration files.
It supports different environments (development, production, test) and loads
the appropriate .env file based on the specified environment.
==============================================================================
"""

import dotenv

def setup_environment(env: str):
    """
    Load environment-specific configuration based on the specified environment.
    
    Args:
        env (str): Environment name (development, production, test, etc.)
    
    Returns:
        bool: True if environment file was loaded successfully, False otherwise
    
    Environment Files:
        - development: env/.env.development
        - production: .env (root level)
        - other: env/{env} (custom environment files)
    """
    if env == "development":
        # =============================================================================
        # Development Environment
        # =============================================================================
        # Load development-specific configuration
        print("Loading development env ")
        return dotenv.load_dotenv("env/.env.development")
    elif env == "production":
        # =============================================================================
        # Production Environment
        # =============================================================================
        # Load production configuration from root .env file
        print("Loading production env ")
        return dotenv.load_dotenv()
    else:
        # =============================================================================
        # Custom Environment
        # =============================================================================
        # Load custom environment-specific configuration
        print("Loading ", env, " environment")
        return dotenv.load_dotenv("env/" + env)
