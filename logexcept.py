from collections import deque
import linecache
import logging
import sys
import traceback


def create_exchook(file=sys.stderr):

    def exchook(etype, value, tb):

        def _get_global_loggers_from_frame(frame_globals):
            # TODO: optimze by looking for common variable
            #       names first, e.g. 'logger' or 'LOGGER'
            return [obj for (name, obj) in frame_globals.items()
                if isinstance(obj, logging.Logger)]

        def _create_log_lines(logs):
            log_msg = '\n    logs:\n'
            for pos, log_record in enumerate(logs):
                log_msg += ' ' * 8
                log_msg += 'line %d, msg: %s' % (log_record.lineno, handler.format(log_record))
                if pos != len(logs) -1:
                    log_msg += '\n'
            return log_msg

        def _extract_traceback(tb):
            # copying what traceback.extract_tb does internally
            f = tb.tb_frame
            co = f.f_code
            linecache.checkcache(co.co_filename)
            line = linecache.getline(co.co_filename, tb.tb_lineno, tb.tb_frame.f_globals)
            line = line.strip() if line else ''
            return (co.co_filename, tb.tb_lineno, co.co_name, line)

        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
        else:
            limit = None

        list = []
        n = 0
        while tb is not None and (limit is None or n < limit):
            frame = tb.tb_frame

            handlers = []
            global_loggers = _get_global_loggers_from_frame(frame.f_globals)
            for logger in global_loggers:
                handlers += [x for x in logger.handlers if isinstance(x, LogCollector)]

            handler = None
            try:
                handler = handlers[0]
            except IndexError:
                pass

            (filename, lineno, fn_name, line) = _extract_traceback(tb)

            if handler:
                logs = [x for x in handler.logs if x.funcName == fn_name]
                if len(logs) > 0:
                    line += _create_log_lines(logs)

            list.append((filename, lineno, fn_name, line))
            tb = tb.tb_next
            n = n+1

        file.write('Traceback (most recent call last):\n')
        map(file.write, traceback.format_list(list))
        map(file.write, traceback.format_exception_only(etype, value))

        handler.logs.clear()

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
