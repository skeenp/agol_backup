# /usr/bin/python3

import os
import logging
from datetime import datetime


def setup(prefix: str, app_dir: str, active: bool = True, level=logging.INFO):
    """Function to setup logger object

    Args:
        prefix (str): Prefix for log file in logs directory
        level ([type], optional): Level used for logging to file. Defaults to logging.INFO.

    Returns:
        [type]: logging object
    """
    # Create log dir if not exists
    log_dir = os.path.join(app_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Setup timestamp
    ts = datetime.now()
    path = f"{prefix}_{ts.strftime('%Y%m%d_%H%M%S')}.log"
    path = os.path.join(log_dir, path)
    # Setup logger
    logging.basicConfig(
        filename=path if active else os.devnull,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    logger = logging.getLogger()
    # Return logging object
    return logger


def post(logger: logging, msg: str, level: int = logging.INFO):
    """Function to quickly print data to console and to the logging object

    Args:
        logger (logging): logging object
        msg (str): Message to send to console and logger
        level (int, optional): Level used to describe message. Defaults to logging.INFO.
    """
    # Update console
    print(msg)
    # Clear out colour formatters
    msg = msg
    # Update log
    logger.log(level, msg)
