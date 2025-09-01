from alembic import context
from alembic.command import upgrade
from alembic.config import Config
from database.core.engine import Engine
from service.logs.logger import logger

"""
This module handles database migrations using Alembic.

It sets up the Alembic configuration programmatically and provides
a function to upgrade the database schema to the latest version.
"""

# Load Alembic configuration
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", Engine.url)


def migrate():
    """
    Perform database migration to the latest version (head).

    This function uses Alembic to apply all pending migrations. It logs
    the migration start and completion.

    Usage:
        Call this function from your application startup script or manually
        to ensure the database schema is up to date.

    Example:
        if __name__ == "__main__":
            migrate()

    Logs:
        - "Migrating database" at start
        - "Database migrated" after successful migration
    """
    logger.info("Migrating database")
    upgrade(alembic_cfg, "head")
    logger.info("Database migrated")
