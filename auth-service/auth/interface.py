from abc import ABC, abstractmethod


class AuthInterface(ABC):
    """
    Abstract base class defining the interface for authentication controllers.

    Any class implementing this interface must provide concrete implementations
    for signing in, logging out, updating user/device info, and session management.

    Methods:
        sign_in(email: str, password: str)
        logout()
        update_user()
        update_device()
        generate_session()
    """

    @abstractmethod
    def sign_in(self, email: str, password: str):
        """
        Authenticate a user with email and password.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            dict: Authentication result, typically including success status and user/session data.
        """
        pass

    @abstractmethod
    def logout(self):
        """
        Log out the currently authenticated user.

        Returns:
            dict: Result of the logout operation, typically including success status.
        """
        pass

    @abstractmethod
    def update_user(self):
        """
        Update the user's profile or account information.

        Returns:
            dict: Result of the update operation, including success status and updated data.
        """
        pass

    @abstractmethod
    def update_device(self):
        """
        Update device information associated with the user.

        Returns:
            dict: Result of the device update, including success status and updated device info.
        """
        pass

    @abstractmethod
    def generate_session(self):
        """
        Generate a new session for the authenticated user.

        Returns:
            dict: Session information, including session ID, fingerprint, and any metadata.
        """
        pass
