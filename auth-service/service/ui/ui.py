from typing import Union

import config.init_config as init_config
import mako.template
from mako.lookup import TemplateLookup
from service.logs.logger import logger


def render_template(template_name: str, **kwargs) -> Union[bytes, str]:
    logger.info(f"Rendering template: {template_name}")
    template_lookup = TemplateLookup(directories=[init_config.template_path])
    template = mako.template.Template(
        filename=init_config.template_path + "/" + template_name, lookup=template_lookup
    )
    logger.info(f"Template rendered: {template_name}")
    return template.render(**kwargs)
