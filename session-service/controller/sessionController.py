from fastapi import APIRouter
from service.session.features.fetch import FetchSession


class SessionController:
    def __init__(self, session_id: str):
        self.session = FetchSession()
        self.session_id = session_id

    def get_session(
        self,
    ):
        session = self.session.fetch_session(self.session_id)
        if session is None or session["response"] == "Session not found":
            return {"message": "Session not found"}

        else:
            return session
