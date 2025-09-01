"""
==============================================================================
AuthFlow Supabase - Simple Authentication Service
==============================================================================
This module provides the core authentication logic for the AuthFlow service.
It handles user registration, login, password reset, and session management
with Supabase integration and device fingerprinting.

Key Features:
- User registration and login
- Password reset functionality
- Device fingerprinting for security
- Session management
- Error handling and logging

Author: AuthFlow Team
Version: 0.1.0
==============================================================================
"""

from typing import Dict

from auth.base import BaseAuth
from controllers.auth_controllers.auth_controller import SimpleAuthController
from controllers.device_controller import DeviceController
from controllers.session_controller import SessionController
from controllers.user_controller import UserController
from fastapi import Request
from service.logs.logger import logger


class SimpleAuth(BaseAuth):
    """
    Simple authentication service that handles user authentication flows.
    
    This class orchestrates the complete authentication process including:
    - User registration and login
    - Device tracking and fingerprinting
    - Session creation and management
    - Error handling and logging
    
    Attributes:
        request (Request): FastAPI request object for extracting device info
        auth_controller (SimpleAuthController): Handles Supabase authentication
        session_controller (SessionController): Manages user sessions
        user_controller (UserController): Handles user data operations
    """
    
    def __init__(self, request: Request):
        """
        Initialize the SimpleAuth service with request context.
        
        Args:
            request (Request): FastAPI request object containing headers and client info
        """
        self.request = request
        self.auth_controller = SimpleAuthController()  # Supabase auth operations
        self.session_controller = SessionController()  # Session management
        self.user_controller = UserController()  # User data operations

    async def update_device(self, user_id: str) -> Dict | str:
        """
        Create or update device information for a user.
        
        Extracts device information from the request (IP, User-Agent, etc.)
        and creates a device record in the database for security tracking.
        
        Args:
            user_id (str): The user's ID for device association
            
        Returns:
            Dict | str: Device information if successful, None if failed
        """
        logger.info(f"Updating device for user: {user_id}")
        
        # Create device controller with request information
        device_controller = DeviceController(
            user_agent=self.request.headers.get("User-Agent"),  # Browser/device info
            accept_language=self.request.headers.get("Accept-Language"),  # Language preference
            ip=self.request.client.host,  # Client IP address
            user_id=int(user_id),  # Associated user ID
        )
        
        # Create device record in database
        device = device_controller.create_device()
        logger.info(f"Device: {device}")
        
        if device["success"] is False:
            logger.error("Failed to create device")
            return None
        if device["success"] is True:
            return device["data"]

    async def update_user(
        self, user_id: str, user_name: str, user_email: str, user_avatar: str
    ) -> Dict | str:
        """
        Create or update user information in the database.
        
        Creates a new user record or updates existing user information
        with data from Supabase authentication response.
        
        Args:
            user_id (str): Supabase user ID
            user_name (str): User's display name
            user_email (str): User's email address
            user_avatar (str): User's avatar URL (optional)
            
        Returns:
            Dict | str: User information if successful, None if failed
        """
        logger.info(f"Creating user: {user_id}")
        print(
            f"User ID: {user_name}, User Email: {user_email}, User Avatar: {user_avatar}, User UUID: {user_id}"
        )
        
        # Create user record in database
        response = await self.user_controller.create_user(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_id,
        )

        if response["success"] is False:
            logger.error("Failed to create user")
            return None
        if response["success"] is True:
            return response["data"]

    async def generate_session(self, user_id: str) -> Dict | str:
        """
        Generate a new session for the authenticated user.
        
        Creates a new session with device fingerprinting and stores it
        in Redis for session management and security tracking.
        
        Args:
            user_id (str): The user's ID for session creation
            
        Returns:
            Dict | str: Session information if successful, None if failed
        """
        # Create session with device fingerprinting
        session = await self.session_controller.create_session(
            request=self.request, user_id=user_id
        )
        
        if session["success"] is False:
            logger.error("Failed to create session")
            return None
        if session["success"] is True:
            return session["data"]
        return session

    async def sign_up_process(self, response: Dict) -> Dict | str:
        """
        Process user registration after successful Supabase signup.
        
        This method handles the complete user registration flow:
        1. Extract user metadata from Supabase response
        2. Create user record in database
        3. Create device record for security tracking
        4. Return success response
        
        Args:
            response (Dict): Supabase authentication response
            
        Returns:
            Dict | str: Registration result with success/error information
        """
        try:
            logger.info("Signing up with email", response)
            
            # Extract user metadata from Supabase response
            user_metadata = response["data"].user.user_metadata
            
            # Create user record in database
            create_user = await self.update_user(
                user_id=response["data"].user.id,
                user_name=user_metadata.get("email"),
                user_email=user_metadata.get("email"),
                user_avatar=None,
            )

            if create_user is None:
                logger.error("Failed to create user")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                    "solution": "If email already exists, please sign in after verifying your email.",
                }

            # Create device record for security tracking
            device_id = await self.update_device(create_user.get("id"))

            if device_id is None:
                logger.error("Failed to create device")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                    "solution": "If email already exists, please sign in after verifying your email.",
                }

            # Return successful registration response
            return {
                "success": True,
                "message": "Sign in successful",
                "data": {
                    "message": "Sign up successful! Kindly check your email for verification."
                },
            }
        except Exception as e:
            logger.error(f"Failed to sign in: {str(e)}")
            return {
                "success": False,
                "message": "Failed to sign in! Please try again later.",
                "error": str(e),
                "solution": "If email already exists, please sign in after verifying your email.",
            }

    async def auth_process(self, response: Dict) -> Dict | str:
        """
        Process user authentication after successful Supabase signin.
        
        This method handles the complete authentication flow:
        1. Extract user metadata from Supabase response
        2. Create/update user record in database
        3. Create device record for security tracking
        4. Generate session for user
        5. Return authentication result
        
        Args:
            response (Dict): Supabase authentication response
            
        Returns:
            Dict | str: Authentication result with session and device information
        """
        try:
            # Extract user metadata from Supabase response
            user_metadata = response["data"].user.user_metadata
            
            # Create/update user record in database
            create_user = await self.update_user(
                user_id=response["data"].user.id,
                user_name=user_metadata.get("email"),
                user_email=user_metadata.get("email"),
                user_avatar=None,
            )

            if create_user is None:
                logger.error("Failed to create user")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                }

            # Create device record for security tracking
            device_id = await self.update_device(create_user.get("id"))

            if device_id is None:
                logger.error("Failed to create device")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                }

            # Generate session for user
            session = await self.generate_session(user_id=create_user.get("id"))

            if session is None:
                logger.error("Failed to generate session")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                }

            # Return successful authentication with session and device info
            return {
                "success": True,
                "message": "Sign in successful",
                "data": {"session": session, "device_id": device_id},
            }
        except Exception as e:
            logger.error(f"Failed to sign in: {str(e)}")
            return {
                "success": False,
                "message": "Failed to sign in! Please try again later.",
                "solution": "If email already exists, please sign in after verifying your email.",
            }

    async def sign_up(self, email: str, password: str) -> Dict | str:
        """
        Register a new user with email and password.
        
        This method handles the complete user registration process:
        1. Call Supabase signup
        2. Process user creation and device tracking
        3. Return registration result
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            Dict | str: Registration result with success/error information
        """
        try:
            logger.info("Signing up with email")
            
            # Call Supabase authentication
            response = self.auth_controller.sign_up(email, password)
            
            if response is None:
                logger.error("Failed to sign up")
                return {
                    "success": False,
                    "message": "Failed to sign up! Please try again later.",
                    "error": "If email already exists, please sign in after verifying your email.",
                }
            
            # Process the signup response
            response = await self.sign_up_process(response)
            return response
        except Exception as e:
            logger.error(f"Failed to sign up: {str(e)}")
            return {
                "success": False,
                "message": "Failed to sign up! Please try again later.",
                "error": str(e),
            }

    async def sign_in(self, email: str, password: str) -> Dict | str:
        """
        Authenticate existing user with email and password.
        
        This method handles the complete user authentication process:
        1. Call Supabase signin
        2. Process user authentication and session creation
        3. Return authentication result with session
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            Dict | str: Authentication result with session information
        """
        try:
            logger.info("Signing in with email")
            
            # Call Supabase authentication
            response = self.auth_controller.sign_in(email, password)

            if response["success"] is False:
                logger.error("Failed to sign in")
                return {
                    "success": False,
                    "message": "Failed to sign in! Either email or password is incorrect.Verify your credentials and try again.",
                }

            # Process the signin response
            response = await self.auth_process(response)
            return response
        except Exception as e:
            logger.error(f"Failed to sign in: {str(e)}")
            return {
                "success": False,
                "message": "Failed to sign in! Please try again later. Verify your credentials and try again by confirming your email.",
                "solution": "If email already exists, please sign in after verifying your email.",
            }

    async def forgot_password(self, email: str) -> Dict | str:
        """
        Send password reset email to user.
        
        Initiates the password reset process by sending a reset email
        to the user's registered email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            Dict | str: Password reset result
        """
        try:
            logger.info("Forgot password")
            response = self.auth_controller.forgot_password(email)
            return response
        except Exception as e:
            logger.error(f"Failed to forgot password: {str(e)}")
            return {
                "success": False,
                "message": "Failed to reset password! Please try again later.",
                "solution": "Check email and try again.",
            }

    async def reset_password(self, password: str) -> Dict | str:
        """
        Reset user's password with new password.
        
        Updates the user's password in Supabase after password reset
        token validation.
        
        Args:
            password (str): New password to set
            
        Returns:
            Dict | str: Password reset result
        """
        try:
            logger.info("Reset password")
            response = self.auth_controller.reset_password(password)
            return response
        except Exception as e:
            logger.error(f"Failed to reset password: {str(e)}")
            return {
                "success": False,
                "message": "Failed to reset password! Please try again later.",
                "solution": "Check email and try again.",
            }
