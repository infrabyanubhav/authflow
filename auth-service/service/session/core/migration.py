import alembic
from alembic.command import upgrade
from alembic.config import Config
from database.core.engine import Engine
from service.logs.logger import logger

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", Engine.url)

upgrade(alembic_cfg, "head")
logger.info("Migration completed")
