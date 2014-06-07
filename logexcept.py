from collections import deque
import linecache
import logging
import sys
import traceback


def create_exchook(file=sys.stderr):

    def exchook(etype, value, tb):

        def _print(str='', terminator='\n'):
            file.write(str + terminator)

        def _get_global_loggers_from_frame(frame):
            # TODO: optimze by looking for common variable
            #       names first, e.g. 'logger' or 'LOGGER'
            return [frame.f_globals[x] for x in frame.f_globals
                if isinstance(frame.f_globals[x], logging.Logger)]

        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
        else:
            limit = None
        list = []
        n = 0
        while tb is not None and (limit is None or n < limit):
            frame = tb.tb_frame

            handlers = []
            global_loggers = _get_global_loggers_from_frame(frame)
            for logger in global_loggers:
                handlers += [x for x in logger.handlers if isinstance(x, LogCollector)]

            handler = None
            try:
                handler = handlers[0]
            except IndexError:
                pass

            # copying what extract_tb does internally
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            if line: line = line.strip()
            else: line = ''

            if handler:
                logs = [x for x in handler.logs if x.funcName == frame.f_code.co_name]
                if len(logs) > 0:
                    new_msg = line + '\n    logs:\n'
                    for log_record in logs:
                        # TODO: don't add newline to end of last msg
                        # TODO: windows newlines
                        x = '        line %d, msg: %s\n' % (log_record.lineno, handler.format(log_record))
                        new_msg += x
                    line = new_msg

            list.append((filename, lineno, name, line))

            tb = tb.tb_next
            n = n+1

        _print('Traceback (most recent call last):\n')
        map(_print, traceback.format_list(list))
        map(_print, traceback.format_exception_only(etype, value))
        # TODO: we can empty the logs in all the handlers now, potential memory leak?

    return exchook


class LogCollector(logging.Handler):

    def __init__(self, log_limit=1000):
        logging.Handler.__init__(self)
        self.logs = deque(maxlen=log_limit)

    def emit(self, record):
        try:
            self.logs.append(record)
        except:
            self.handleError(record)
