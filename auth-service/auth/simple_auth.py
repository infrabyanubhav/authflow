from typing import Dict

from auth.base import BaseAuth
from controllers.auth_controllers.auth_controller import SimpleAuthController
from controllers.device_controller import DeviceController
from controllers.session_controller import SessionController
from controllers.user_controller import UserController
from fastapi import Request
from service.logs.logger import logger


class SimpleAuth(BaseAuth):
    def __init__(self, request: Request):
        self.request = request
        self.auth_controller = SimpleAuthController()
        self.session_controller = SessionController()
        self.user_controller = UserController()

    async def update_device(self, user_id: str) -> Dict | str:
        logger.info(f"Updating device for user: {user_id}")
        device_controller = DeviceController(
            user_agent=self.request.headers.get("User-Agent"),
            accept_language=self.request.headers.get("Accept-Language"),
            ip=self.request.client.host,
            user_id=int(user_id),
        )
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
        logger.info(f"Creating user: {user_id}")
        print(
            f"User ID: {user_name}, User Email: {user_email}, User Avatar: {user_avatar}, User UUID: {user_id}"
        )
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
        try:
            logger.info("Signing up with email", response)
            user_metadata = response["data"].user.user_metadata
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

            device_id = await self.update_device(create_user.get("id"))

            if device_id is None:
                logger.error("Failed to create device")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                    "solution": "If email already exists, please sign in after verifying your email.",
                }

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
        try:
            user_metadata = response["data"].user.user_metadata
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

            device_id = await self.update_device(create_user.get("id"))

            if device_id is None:
                logger.error("Failed to create device")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                }

            session = await self.generate_session(user_id=create_user.get("id"))

            if session is None:
                logger.error("Failed to generate session")
                return {
                    "success": False,
                    "message": "Failed to sign in! Please try again later.",
                }

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
        try:
            logger.info("Signing up with email")
            response = self.auth_controller.sign_up(email, password)
            if response is None:
                logger.error("Failed to sign up")
                return {
                    "success": False,
                    "message": "Failed to sign up! Please try again later.",
                    "error": "If email already exists, please sign in after verifying your email.",
                }
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
        try:
            logger.info("Signing in with email")
            response = self.auth_controller.sign_in(email, password)

            if response["success"] is False:
                logger.error("Failed to sign in")
                return {
                    "success": False,
                    "message": "Failed to sign in! Either email or password is incorrect.Verify your credentials and try again.",
                }

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
