"""Handles configuration and logging."""

import logging
import sys
import time
from datetime import timedelta
from logging import FileHandler, Formatter, StreamHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "images"

IMAGE_INTERVAL = timedelta(seconds=10)
RUN_DURATION = timedelta(minutes=9)

IMAGE_LOOKBEHIND = 2
PERCENTAGE_ERROR = 25
ANOMALOUS_DEVIATION = 2
MIN_IMAGE_MATCHES = 100
MIN_SPEEDS = 5

VIEW_MATCHES = False
VIEW_RESOLUTION = (1600, 600)


def setup_logging() -> None:
    logging.Formatter.converter = time.gmtime

    simple_formatter = Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    colored_formatter = Formatter(
        (
            "\u001b[90m%(asctime)s\u001b[0m "
            + "\u001b[34m%(levelname)-8s\u001b[0m "
            + "\u001b[32m%(name)-15s \u001b[0m %(message)s"
        ),
        "%Y-%m-%d %H:%M:%S",
    )

    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(colored_formatter)

    file_handler = FileHandler(BASE_DIR / "info.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(simple_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
