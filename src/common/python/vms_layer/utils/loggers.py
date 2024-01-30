import logging
import sys

from vms_layer.config.config import LOG_CONFIG


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG.get("LOG_LEVEL", "INFO"))
    formatter = logging.Formatter(
        LOG_CONFIG.get(
            "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        LOG_CONFIG.get("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S"),
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
