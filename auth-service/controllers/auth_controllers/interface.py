from abc import ABC, abstractmethod


class AuthControllerInterface(ABC):
    """
    Interface for authentication controllers.

    This abstract base class defines the essential methods that any
    authentication controller must implement. Subclasses must provide
    concrete implementations for signing in and signing out users.
    """

    @abstractmethod
    def sign_in(self, email: str, password: str):
        """
        Authenticate a user with the given email and password.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            dict | None: A dictionary containing authentication results
            (e.g., success status, tokens) if authentication succeeds,
            otherwise None.
        """
        pass

    @abstractmethod
    def sign_out(self):
        """
        Log out the currently authenticated user.

        Returns:
            dict | None: A dictionary containing logout results
            (e.g., success status) if sign-out succeeds, otherwise None.
        """
        pass
