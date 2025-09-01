from customExceptions.controller_exception import ControllerException
from database.crud.device_info import create_device_info
from database.models.device_info import DeviceInfo
from schema.device_schema import DeviceSchema
from service.logs.logger import logger


class DeviceController:
    """
    Controller to handle device validation and creation for a user.

    Attributes:
        user_agent (str): User agent string from the request.
        accept_language (str): Accepted language header from the request.
        ip (str): IP address of the user.
        user_id (int): ID of the authenticated user.
    """

    def __init__(self, user_agent: str, accept_language: str, ip: str, user_id: int):
        """
        Initialize the DeviceController with user and request information.

        Args:
            user_agent (str): User agent string from the request.
            accept_language (str): Accepted language header.
            ip (str): User IP address.
            user_id (int): Authenticated user's ID.
        """
        self.user_agent = user_agent
        self.accept_language = accept_language
        self.ip = ip
        self.user_id = user_id

    def validate_device(self) -> dict:
        """
        Validate device information provided by the user.

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether validation succeeded.
                - message (str): Description of validation result.
                - data (DeviceSchema, optional): Validated device schema if successful.
        """
        logger.info("Validating device")
        try:
            device = DeviceSchema(
                user_agent=self.user_agent,
                accept_language=self.accept_language,
                ip=self.ip,
                user_id=self.user_id,
            )
            if device is None:
                return {"success": False, "message": "Device is None"}
            return {
                "success": True,
                "message": "Device validated successfully",
                "data": device,
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error validating device: %s", ControllerException(str(e)))
            return {
                "success": False,
                "message": "Error validating device! Please try again later.",
            }

    def create_device(self) -> dict:
        """
        Validate and create a new device entry for the user.

        This method first validates the device using `validate_device`.
        If validation passes, it creates a `DeviceInfo` record in the database.

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the device was created successfully.
                - message (str): Description of the result.
                - data (dict, optional): Device data (user_agent, accept_language, ip) if created.
        """
        logger.info("Creating device")
        try:
            device_result = self.validate_device()
            if not device_result["success"]:
                return device_result  # Return the validation error

            device = device_result["data"]
            device_info = DeviceInfo(
                user_agent=device.user_agent,
                accept_language=device.accept_language,
                ip=device.ip,
                user_id=device.user_id,
            )

            added_device = create_device_info(device_info)
            if added_device is not None:
                self.device_data = {
                    "user_agent": device.user_agent,
                    "accept_language": device.accept_language,
                    "ip": device.ip,
                }
                return {
                    "success": True,
                    "message": "Device created successfully",
                    "data": self.device_data,
                }
            else:
                return {"success": False, "message": "Error adding device"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error creating device: %s", ControllerException(str(e)))
            return {
                "success": False,
                "message": "Error creating device! Please try again later.",
            }
