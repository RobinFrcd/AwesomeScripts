import logging
import os
import sys

import colorlog
from pynput.keyboard import Key

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()


def get_key_str(key: Key) -> str:
    try:
        return key.char
    except AttributeError:
        return key.name


def set_logger():
    handler = colorlog.StreamHandler(
        stream=sys.stdout,
    )
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "$log_color$asctime $name[$lineno] $bold$levelname$reset $message_log_color$message",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={
                "message": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            },
            style="$",
        )
    )

    logging.basicConfig(
        handlers=[handler],
        level=LOG_LEVEL,
    )
