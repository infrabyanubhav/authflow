import config.init_config as config
from service.logs.logger import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

"""
This module sets up the SQLAlchemy database engine, session, and base model.

It configures connection pooling, performance optimizations, and provides
a generator function for database sessions.
"""

# Optimized engine with connection pooling
Engine = create_engine(
    config.db_config["url"],
    echo=True,
    # Connection Pool Configuration
    pool_size=10,  # Keep 10 connections in pool
    max_overflow=20,  # Allow 20 extra connections when busy
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=30,  # Wait 30s for connection from pool
    # Performance Optimizations
)

# SQLAlchemy session factory
Session = sessionmaker(bind=Engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Generator function to provide a database session.

    Yields:
        sqlalchemy.orm.Session: SQLAlchemy session instance.

    Behavior:
        - Creates a new database session.
        - Yields the session to the caller.
        - Ensures the session is closed after use, returning the connection
          to the pool.
        - Logs creation and closing of the session.

    Example:
        async def some_route(db: Session = Depends(get_db)):
            user = db.query(User).first()
            return user
    """
    db = Session()
    logger.info("Database session created")
    try:
        yield db
    finally:
        db.close()  # Returns connection to pool, doesn't destroy it
        logger.info("Database session closed")
