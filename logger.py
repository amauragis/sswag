import colorlog
import logging
import sys

formatter = colorlog.ColoredFormatter(
    '{log_color}{levelname:8}{reset} {message}',
    datefmt=None,
    style="{",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
    }
)

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(formatter)

l = logging.getLogger()
l.setLevel(logging.DEBUG)
l.addHandler(stream)


def debug(s):
    l.debug(s)


def info(s):
    l.info(s)


def warn(s):
    l.warning(s)


def error(s):
    l.error(s)


def critical(s):
    l.critical(s)
    l.critical('')
    l.critical('Critical error. Website NOT successfully built. Quitting.')
    sys.exit(1)


def critical_leader(s):
    l.critical(s)
