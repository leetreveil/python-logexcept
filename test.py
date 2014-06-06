import logging
import sys
from logexcept import create_exchook, LogCollector
from b import foo


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(LogCollector())

sys.excepthook = create_exchook()

def some_other_function():
    logger.info('in some_other_function')
    some_function()

def some_function():
    logger.debug('%s %s' % ('a', 'b'));
    logger.info('in some_function!')
    foo()

some_other_function()
