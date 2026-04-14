import logging
import logging.config
import os
import yaml
from shared.config import settings

def init_logger(name : str = "default"):
    log = None
    path_route = os.path.abspath("logging.yml")
    with open(path_route, 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    
    log = logging.getLogger(f"{settings.LOG_NAME}.{name}")
    
    return log