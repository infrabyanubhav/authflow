from service.logs.logger import logger
from service.supabase_client.supabase_auth import SimpleAuth

"""
This controller handles authentication operations by interacting with the
SimpleAuth service. It provides higher-level functions for signing up, 
signing in, signing out, and handling password resets, while also logging 
each action for monitoring purposes.
"""


class SimpleAuthController:
    def __init__(self):
        """
        Initialize the SimpleAuthController.

        Creates an instance of the SimpleAuth service to delegate
        authentication operations.
        """
        self.simple_auth = SimpleAuth()

    def sign_up(self, email: str, password: str):
        """
        Register a new user with the given email and password.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            dict | None: Returns the response dictionary if sign-up is
            successful, otherwise None.
        """
        logger.info("Signing up user with email")

        if email is None or password is None:
            return None

        response = self.simple_auth.sign_up(email, password)
        if isinstance(response, dict):
            return response

    def sign_in(self, email: str, password: str):
        """
        Authenticate a user with the given email and password.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            dict | None: Returns the response dictionary if sign-in is
            successful, otherwise None.
        """
        logger.info("Signing in user with email")
        if email is None or password is None:
            return None
        response = self.simple_auth.sign_in(email, password)
        if response["success"]:
            return response

    def sign_out(self):
        """
        Log out the currently authenticated user.

        Returns:
            dict | None: Returns the response dictionary if sign-out is
            successful, otherwise None.
        """
        logger.info("Signing out user")
        response = self.simple_auth.sign_out()
        if response["success"]:
            return response

    def forgot_password(self, email: str):
        """
        Trigger the forgot password process for the given email.

        Args:
            email (str): User's email address.

        Returns:
            dict | None: Returns the response dictionary if the process is
            successful, otherwise None.
        """
        logger.info("Forgot password")
        if email is None:
            return None
        response = self.simple_auth.forgot_password(email)
        if response["success"]:
            return response

    def reset_password(self, password: str):
        """
        Reset the user's password.

        Args:
            password (str): The new password to set.

        Returns:
            dict | None: Returns the response dictionary if reset is
            successful, otherwise None.
        """
        logger.info("Reset password")
        if password is None:
            return None
        response = self.simple_auth.reset_password(password)
        if response["success"]:
            return response
