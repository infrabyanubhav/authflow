from database.core.engine import Session
from service.logs.logger import logger


def atomic_transaction(func):
    """
    Decorator for atomic database transactions.

    Wraps a function execution within a database session, ensuring that
    all operations are committed if successful, or rolled back in case of errors.

    Args:
        func (Callable): Function to be executed atomically. The first argument
                         passed to the function will be the database session.

    Returns:
        Callable: Wrapped function that manages session lifecycle automatically.

    Behavior:
        - Creates a new database session.
        - Passes the session as the first argument to the decorated function.
        - Commits the transaction if the function executes successfully.
        - Rolls back the transaction if an exception is raised.
        - Closes the session in all cases.

    Example:
        @atomic_transaction
        def create_user(db, user_data):
            db.add(user_data)
            return user_data
    """

    def wrapper(*args, **kwargs):
        db = Session()
        try:
            # Call the function with the database session as first argument
            result = func(db, *args, **kwargs)

            # Commit the transaction
            db.commit()
            logger.info(f"Atomic transaction completed for {func.__name__}")
            return result

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Rollback on error
            db.rollback()
            raise e
        finally:
            # Always close the session
            logger.info(f"Closing database session for {func.__name__}")
            db.close()

    return wrapper
