import re

from pydantic import BaseModel

"""
This class is used to validate the input of the user
"""


class AuthInput(BaseModel):  # pylint: disable=too-few-public-methods
    """
    This class is used to validate the input of the user
    """

    email: str
    password: str


async def validate_input(input: AuthInput) -> AuthInput:
    """
    This function is used to validate the input of the user
    """
    if input.email is None or input.password is None:
        return None
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", input.email):
        return None
    if len(input.password) < 12:
        return None
    if not any(char.isupper() for char in input.password):
        return None
    if not any(char.islower() for char in input.password):
        return None
    if not any(char.isdigit() for char in input.password):
        return None

    return input
