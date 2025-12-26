import logging
import logging.config
import os
import yaml

def init_logger(nameLogger):
    log = None
    path_route = os.path.abspath("logging.yml")
    with open(path_route, 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        log = logging.getLogger(nameLogger)
    
    return log