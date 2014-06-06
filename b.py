import logging
from logexcept import LogCollector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

hdlr = LogCollector(log_limit=10)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

def foo():
    logger.info("we are in foo!")
    for x in range(0, 20):
        logger.info("we are in foo!")
    raise Exception('poop')
