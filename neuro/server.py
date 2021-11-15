import logging
from concurrent.futures.thread import ThreadPoolExecutor

import click
import tornado.ioloop
import tornado.web

from .app import make_app

logger = logging.getLogger(__name__)


def setup_logger():
    """Initializes the root logger"""
    logging.basicConfig(
        level=logging.INFO,
        format="[ %(asctime)s.%(msecs)03d ][ %(levelname)s ][ %(name)s ] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def set_logging_level(verbosity: int):
    """Sets logging level for the root logger"""
    level = 10 * (5 - verbosity)
    logger.info("Logging level set to %s", logging.getLevelName(level))
    logging.getLogger().setLevel(level)


@click.command()
@click.option("-v", "--verbosity", default=3, envvar="LOG_VERBOSITY")
@click.option("-p", "--port", default=3003, envvar="PORT")
@click.option("-w", "--workers", default=4, envvar="WORKERS")
def main(**settings):
    """Call processing job"""
    setup_logger()
    set_logging_level(settings["verbosity"])
    worker_limit = settings["workers"]
    executor = ThreadPoolExecutor(max_workers=worker_limit)
    logger.info("worker limit set to %d", worker_limit)
    port = int(settings["port"])
    app = make_app(executor)
    app.listen(port)
    logger.info("listening on port %d", port)
    loop = tornado.ioloop.IOLoop.current()
    loop.set_default_executor(executor)
    loop.start()
