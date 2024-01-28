"""Logger module for task3_dsw."""

import logging
import sys

from task3_dsw import settings

logger = logging.getLogger("Task3 DSW Logger")

stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter(
    "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s"
)

stdout.setFormatter(fmt)
logger.addHandler(stdout)

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)
