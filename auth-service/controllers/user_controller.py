from customExceptions.controller_exception import ControllerException
from database.crud.user import create_user, get_user
from database.models.user import User
from schema.user_schema import UserSchema
from service.logs.logger import logger


class UserController:
    """
    Controller for managing user operations such as validation, creation, and retrieval.

    Handles the complete lifecycle of user entities, including schema validation,
    database creation, and lookup operations.
    """

    def __init__(self):
        """
        Initialize the UserController.

        Currently, no instance attributes are required at initialization.
        """
        pass

    async def validate_user(self, user_name: str, user_email: str) -> dict:
        """
        Validate user data using Pydantic schema.

        Args:
            user_name (str): Name of the user to validate.
            user_email (str): Email of the user to validate.

        Returns:
            dict: Dictionary with validation result:
                - success (bool): Whether the validation was successful.
                - message (str): Human-readable status message.
                - data (UserSchema, optional): Validated user data.
        """
        try:
            user_schema = UserSchema(
                user_name=user_name,
                user_email=user_email,
            )
            validated_data = user_schema.validate_all()
            if validated_data is None:
                logger.error(
                    "User validation failed: %s",
                    ControllerException("User validation failed"),
                )
                return {
                    "success": False,
                    "message": "User validation failed! Please try again later.",
                }
            logger.info(f"User validation successful: {validated_data.user_name}")
            return {
                "success": True,
                "message": "User validation successful",
                "data": validated_data,
            }
        except Exception as e:
            logger.error("Error validating user: %s", ControllerException(str(e)))
            return {
                "success": False,
                "message": "Error validating user! Please try again later.",
            }

    async def create_user(
        self,
        user_name: str,
        user_email: str,
        user_avatar: str = None,
        user_uuid: str = None,
    ) -> dict:
        """
        Create a new user in the database.

        Validates the user data, checks for existing users, and creates a new user
        record if none exists.

        Args:
            user_name (str): Name of the user.
            user_email (str): Email of the user.
            user_avatar (str, optional): Avatar URL for the user.
            user_uuid (str, optional): UUID for the user.

        Returns:
            dict: Dictionary with creation result:
                - success (bool): Whether the creation was successful.
                - message (str): Human-readable status message.
                - data (User, optional): Created or existing user data.
        """
        try:
            # Validate user data
            validation_result = await self.validate_user(user_name, user_email)
            if not validation_result["success"]:
                return validation_result  # Return validation error

            logger.info("User data validated successfully")
            validated_data = validation_result["data"]

            # Check if user already exists
            existing_user = get_user(validated_data.user_email)
            if existing_user is not None:
                logger.info("User already exists")
                return {
                    "success": True,
                    "message": "User already exists",
                    "data": existing_user,
                }

            # Create new User model instance
            logger.info("Creating User model instance")
            user_model = User(
                user_name=validated_data.user_name,
                user_email=validated_data.user_email,
                user_avatar=user_avatar,
                user_uuid=user_uuid,
            )
            logger.info("User model created")

            logger.info("Saving user to database")
            created_user = create_user(user_model)

            return {
                "success": True,
                "message": "User created successfully",
                "data": created_user,
            }

        except Exception as e:
            logger.error("Error creating user: %s", ControllerException(str(e)))
            return {
                "success": False,
                "message": "Error creating user! Please try again later.",
            }

    async def get_user(self, user_id: str) -> dict:
        """
        Retrieve a user from the database by user ID.

        Args:
            user_id (str): Identifier for the user to retrieve.

        Returns:
            dict: Dictionary with retrieval result:
                - success (bool): Whether the retrieval was successful.
                - message (str): Human-readable status message.
                - data (User, optional): Retrieved user data if found.
        """
        try:
            user = get_user(user_id)
            if user is not None:
                return {
                    "success": True,
                    "message": "User retrieved successfully",
                    "data": user,
                }
            else:
                return {"success": False, "message": "User not found"}
        except Exception as e:
            logger.error("Error getting user: %s", ControllerException(str(e)))
            return {
                "success": False,
                "message": "Error getting user! Please try again later.",
            }
