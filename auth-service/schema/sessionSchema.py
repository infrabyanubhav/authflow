from pydantic import BaseModel, field_validator


class SessionSchema(BaseModel):  # pylint: disable=too-few-public-methods
    session_id: str
    fingerprint: str
    user_id: int

    @field_validator("session_id")
    def validate_session_id(cls, v):
        if v == "" or v is None:
            raise ValueError("Session ID is required")
        return v

    @field_validator("fingerprint")
    def validate_fingerprint(cls, v):
        if v == "":
            raise ValueError("Fingerprint is required")
        return v

    def validate_all(self):
        self.session_id = self.validate_session_id(self.session_id)
        if self.session_id is None:
            raise ValueError("Session ID is required")
        self.fingerprint = self.validate_fingerprint(self.fingerprint)
        if self.fingerprint is None:
            raise ValueError("Fingerprint is required")
        return {
            "session_id": self.session_id,
            "fingerprint": self.fingerprint,
            "user_id": self.user_id,
        }
