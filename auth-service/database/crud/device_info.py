from typing import Optional

from database.core.atomic import atomic_transaction
from database.core.engine import Session as db_session
from database.models.device_info import DeviceInfo
from service.logs.logger import logger
from sqlalchemy.orm import Session


@atomic_transaction
def create_device_info(db: Session, device_info: DeviceInfo):
    db.add(device_info)
    db.flush()
    logger.info("Device info created")
    return device_info


def get_device_info(ip: str) -> Optional[dict]:
    """Get device info by IP address - creates its own session and returns detached data"""
    db = db_session()
    try:
        existing_device = db.query(DeviceInfo).filter_by(ip=ip).first()
        if existing_device is not None:
            logger.info("Existing device info found for IP: %s", ip)
            # Create a detached copy with all the data
            device_data = {
                "id": existing_device.id,
                "ip": existing_device.ip,
                "user_id": existing_device.user_id,
                "user_agent": existing_device.user_agent,
                "accept_language": existing_device.accept_language,
                "created_at": existing_device.created_at,
                "updated_at": existing_device.updated_at,
            }
            return device_data
        else:
            logger.info("No device info found for IP: %s", ip)
            return None
    except Exception as e:
        logger.error("Error getting device info: %s", e)
        raise e
    finally:
        db.close()
