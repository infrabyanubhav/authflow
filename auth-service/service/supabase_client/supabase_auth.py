from config.init_config import supabase_config
from service.logs.logger import logger
from service.supabase_client.base import SupabaseClient


class SimpleAuth(SupabaseClient):
    """
    Simple authentication class using Supabase for email/password based authentication.

    Provides methods for sign up, sign in, sign out, password reset, and related
    authentication operations. Logs all operations for monitoring purposes.
    """

    def __init__(self):
        """
        Initialize the SimpleAuth client.

        Sets up the request body dictionary used for authentication operations.
        """
        super().__init__()
        self.body = {"email": None, "password": None}

    def simple_auth(self, email: str, password: str) -> dict:
        """
        Authenticate a user with email and password (low-level method).

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            dict: Dictionary containing success status, error message (if any),
                  and response data from Supabase.
        """
        try:
            logger.info("Signing in with email and password")
            self.body["email"] = email
            self.body["password"] = password

            response = self.supabase.auth.sign_in_with_password(self.body)

            if response is not None:
                if hasattr(response, "error") and response.error is not None:
                    logger.error(f"Authentication failed: {response.error.message}")
                    return {
                        "success": False,
                        "error": response.error.message,
                        "data": None,
                    }
                logger.info("Authentication successful")
                return {"success": True, "error": None, "data": response}
            else:
                logger.error("No response received from authentication")
                return {
                    "success": False,
                    "error": "No response received from authentication service",
                    "data": None,
                }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Authentication error: {str(e)}")
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}",
                "data": None,
            }

    def sign_up(self, email: str, password: str) -> dict:
        """
        Register a new user with email and password.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            dict: Dictionary containing success status, error message (if any),
                  and response data from Supabase.
        """
        try:
            logger.info("Signing up with email and password")
            self.body["email"] = email
            self.body["password"] = password

            response = self.supabase.auth.sign_up(self.body)

            if response is not None:
                if hasattr(response, "error") and response.error is not None:
                    logger.error(f"Sign up failed: {response.error.message}")
                    return {
                        "success": False,
                        "error": response.error.message,
                        "data": None,
                    }
                logger.info("Sign up successful")
                return {"success": True, "error": None, "data": response}
            else:
                logger.error("No response received from sign up")
                return {
                    "success": False,
                    "error": "No response received from sign up service",
                    "data": None,
                }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Sign up error: {str(e)}")
            return {
                "success": False,
                "error": f"Sign up failed: {str(e)}",
                "data": None,
            }

    def sign_out(self) -> dict:
        """
        Sign out the currently authenticated user.

        Returns:
            dict: Dictionary containing success status, error message (if any),
                  and response data from Supabase.
        """
        try:
            logger.info("Signing out")
            response = self.supabase.auth.sign_out()
            logger.info(f"Sign out response: {response}")

            if response is not None:
                logger.info("Sign out successful")
                return {"success": True, "error": None, "data": response}
            else:
                logger.error("No response received from sign out")
                return {
                    "success": False,
                    "error": "No response received from sign out service",
                    "data": None,
                }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Sign out error: {str(e)}")
            return {
                "success": False,
                "error": f"Sign out failed: {str(e)}",
                "data": None,
            }

    def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in a user using email and password.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            dict: Dictionary containing success status, error message (if any),
                  and response data from Supabase.
        """
        try:
            logger.info("Signing in with email and password")
            self.body["email"] = email
            self.body["password"] = password
            response = self.supabase.auth.sign_in_with_password(self.body)
            if response is not None:
                if hasattr(response, "error") and response.error is not None:
                    logger.error(f"Sign in failed: {response.error.message}")
                    return {
                        "success": False,
                        "error": response.error.message,
                        "data": None,
                    }
                logger.info("Sign in successful")
                return {"success": True, "error": None, "data": response}
            else:
                logger.error("No response received from sign in")
                return {
                    "success": False,
                    "error": "No response received from sign in service",
                    "data": None,
                }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Sign in error: {str(e)}")
            return {
                "success": False,
                "error": f"Sign in failed: {str(e)}",
                "data": None,
            }

    def forgot_password(self, email: str) -> dict:
        """
        Trigger a password reset email for the given user email.

        Args:
            email (str): User's email address.

        Returns:
            dict: Dictionary containing success status and error message if any.
        """
        try:
            logger.info("Forgot password")
            response = self.supabase.auth.reset_password_for_email(
                email,
                {"redirect_to": supabase_config.get("reset_password_redirect_to")},
            )
            logger.info(f"Forgot password response: {response}")
            return {"success": True, "error": None, "data": response}
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Forgot password error: {str(e)}")
            return {
                "success": False,
                "error": f"Forgot password failed: {str(e)}",
                "data": None,
            }

    def reset_password(self, password: str) -> dict:
        """
        Reset the authenticated user's password.

        Args:
            password (str): New password to set.

        Returns:
            dict: Dictionary containing success status and error message if any.
        """
        try:
            logger.info("Reset password")
            response = self.supabase.auth.update_user(
                {
                    "password": password,
                }
            )
            logger.info(f"Reset password response: {response}")
            return {"success": True, "error": None, "data": response}
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Reset password error: {str(e)}")
            return {
                "success": False,
                "error": f"Reset password failed: {str(e)}",
                "data": None,
            }
