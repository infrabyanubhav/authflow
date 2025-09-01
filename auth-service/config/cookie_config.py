from fastapi.responses import RedirectResponse
from config.init_config import cookie_config
from service.logs.logger import logger
from datetime import datetime

cookie_config = {
    "path": cookie_config["cookie_path"],
    "max_age": cookie_config["cookie_max_age"],
    "secure": cookie_config["cookie_secure"],
    "samesite": cookie_config["cookie_samesite"],
    "httponly": cookie_config["cookie_httponly"],
    "expires":3600,
}




async def set_cookie(response: RedirectResponse, **kwargs):
    response.set_cookie(
        **cookie_config,
        **kwargs,
    )
    logger.info(f"Cookie set: {kwargs}", "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



def delete_cookie(response: RedirectResponse):
    response.delete_cookie(
        **cookie_config,
        )
    logger.info(f"Cookie deleted", "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return response