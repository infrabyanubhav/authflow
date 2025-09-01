from pydantic import BaseModel, field_validator


class UserSchema(BaseModel):  # pylint: disable=too-few-public-methods
    """
    This class is used to validate the input of the user
    """

    user_name: str
    user_email: str

    @field_validator("user_name")
    def validate_user_name(cls, v):
        """
        This function is used to validate the user name
        """
        return v

    @field_validator("user_email")
    def validate_user_email(cls, v):
        """
        This function is used to validate the user email
        """
        return v

    def validate_all(self):
        """
        This function is used to validate the input of the user
        """
        self.user_name = self.validate_user_name(self.user_name)
        self.user_email = self.validate_user_email(self.user_email)
        return self
