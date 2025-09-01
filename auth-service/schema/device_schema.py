import re

from pydantic import BaseModel, field_validator


class DeviceSchema(BaseModel):  # pylint: disable=too-few-public-methods
    """
    This class is used to validate the input of the user
    """

    user_agent: str
    accept_language: str
    ip: str
    user_id: int

    @field_validator("ip")
    def validate_ip(cls, v: str):
        """
        This function is used to validate the IP address
        """
        # Basic IPv4 regex check
        pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid IP address format")

        # Ensure each octet is 0–255
        parts = v.split(".")
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError("IP address octets must be between 0 and 255")

        return v

    @field_validator("user_id")
    def validate_user_id(cls, v):
        """
        This function is used to validate the user ID
        """
        if v is None:
            raise ValueError("User ID is required")
        return v

    def validate_all(self):
        """
        This function is used to validate the input of the user
        """
        self.ip = self.validate_ip(self.ip)
        if self.ip is None:
            raise ValueError("IP is required")
        self.user_id = self.validate_user_id(self.user_id)
        if self.user_id is None:
            raise ValueError("User ID is required")
        return self
