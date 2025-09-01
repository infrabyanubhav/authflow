import uuid


def create_session():
    session_id = uuid.uuid4()
    session_key = f"{session_id}"
    return session_key
