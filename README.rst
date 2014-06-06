Logexcept
-----

Logexcept adds super useful logging messages to your tracebacks:

.. code:: bash

    Traceback (most recent call last):
      File "poop.py", line 17, in <module>
        raise Exception('poop')
        logs:
            line 16, msg: hello!
    Exception: poop

Usage
-----

.. code:: python

    import logging
    import sys
    from logexcept import create_exchook, LogCollector

    # add the log handler, this will intercept log
    # messages and pass them to the exception handler when
    # an exception occurs
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(LogCollector())

    # install our exception handler
    sys.excepthook = create_exchook()

    # lets trigger an exception
    logger.info('hello!')
    raise Exception('poop')

API
----
TODO

Django
-----
TODO


Licence
----
MIT
