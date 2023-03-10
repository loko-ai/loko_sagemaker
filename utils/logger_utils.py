import logging
import sys

fmt = '%(levelname)s - %(message)s  - %(name)s:%(lineno)d - date:%(asctime)s'


def stream_logger(name, fmt=fmt, out=sys.stderr, level=logging.DEBUG):
    logger = logging.getLogger(name.replace(".", "/") + ".py")
    logger.setLevel(level)
    sh = logging.StreamHandler(out)
    sh.setFormatter(logging.Formatter(fmt=fmt, datefmt='%d-%m-%Y:%H:%M:%S'))
    logger.addHandler(sh)

    return logger