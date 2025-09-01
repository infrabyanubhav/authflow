import uuid
from typing import Dict

from customExceptions.controller_exception import ControllerException
from fastapi import Request
from schema.sessionSchema import SessionSchema
from service.logs.logger import logger
from service.security.core.fingerprint import generate_fingerprint
from service.session.features.delete import DeleteSession
from service.session.features.save import SaveSession
from utils.extract_info import extract_info


class SessionController:
    """
    Manages user session operations including creation, generation, and deletion.

    This controller handles the complete lifecycle of user sessions, including
    device fingerprinting, session storage, and cleanup operations.

    Attributes:
        save_session (SaveSession): Instance for persisting session data.
        session_data (dict): Dictionary to store temporary session information.
    """

    def __init__(self):
        """
        Initialize the SessionController with required dependencies.

        Creates instances of SaveSession for data persistence and initializes
        an empty session_data dictionary for temporary storage.
        """
        self.save_session = SaveSession()
        self.session_data = {}

    async def generate_session(self, request: Request) -> dict:
        """
        Generate a new session with device fingerprinting and unique session ID.

        This method creates a new session by extracting device information from the request,
        generating a unique fingerprint, and creating a session ID. It handles error cases
        gracefully and returns structured responses.

        Args:
            request (Request): FastAPI request object containing headers and client info.

        Returns:
            dict: Response dictionary with success status, message, and session data
                - success (bool): Whether the operation succeeded
                - message (str): Human-readable status message
                - data (dict, optional): Session information including:
                    - session_id (str): Unique UUID for the session
                    - fingerprint (str): Device fingerprint hash
                    - info (dict): Extracted device information

        Raises:
            Exception: Propagates any exceptions from extract_info or generate_fingerprint.
        """
        logger.info("Generating session")
        session_id = str(uuid.uuid4())
        info = await extract_info(request)
        logger.info("Info: extracted")
        if not request:
            logger.error("Invalid request, Error Creating Session")
            return {
                "success": False,
                "message": "Invalid request, Error Creating Session",
            }

        fingerprint = await generate_fingerprint(info)
        if fingerprint is None:
            logger.error("Invalid request, Error Creating Session")
            return {
                "success": False,
                "message": "Invalid request, Error Creating Session! Please try again later.",
            }

        try:
            logger.info("Generating session")
            session_values = {
                "fingerprint": fingerprint,
                "session_id": session_id,
                "info": info,
            }
            return {
                "success": True,
                "message": "Session generated successfully",
                "data": session_values,
            }

        except Exception as e:
            logger.error(f"Error generating session: {str(e)}")
            return {
                "success": False,
                "message": "Error generating session! Please try again later.",
            }

    async def create_session(self, request: Request, user_id: str) -> Dict:
        """
        Create and persist a new user session.

        This method generates a session, validates it using SessionSchema, and then
        saves it using SaveSession. Returns structured responses indicating success or failure.

        Args:
            request (Request): FastAPI request object.
            user_id (str): ID of the user for whom the session is being created.

        Returns:
            dict: Response dictionary with success status, message, and session data
                  if creation succeeds.
        """
        logger.info("Creating session")
        try:
            session_values = await self.generate_session(request)
            session_values = session_values["data"]

            session = SessionSchema(
                session_id=session_values.get("session_id"),
                fingerprint=session_values.get("fingerprint"),
                user_id=user_id,
            )

            session = session.validate_all()

            session_keys = {
                "fingerprint": session.get("fingerprint"),
                "user_id": session.get("user_id"),
            }

            await self.save_session.save_session(
                session.get("session_id"), session_keys
            )

            if session is None:
                logger.error("Invalid session", ControllerException("Invalid session"))
                return {
                    "success": False,
                    "message": "Invalid session! Please try again later.",
                }
            logger.info("Session created successfully")
            return {
                "success": True,
                "message": "Session created successfully",
                "data": session,
            }
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return {
                "success": False,
                "message": "Error creating session! Please try again later.",
            }

    async def delete_session(self, request: Request):
        """
        Delete an existing session using the session_id from request cookies.

        Args:
            request (Request): FastAPI request object containing cookies.

        Returns:
            None: Returns None regardless of success or failure.

        Logs:
            Any errors encountered during session deletion.
        """
        logger.info("Deleting session")
        try:
            session_id = request.cookies.get("session_id")
            delete_session = DeleteSession()
            await delete_session.delete_session(session_id)
            if session_id is None:
                logger.error("Invalid request, Error Deleting Session")
                return None
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return None
