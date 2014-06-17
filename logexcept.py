from collections import deque
import linecache
import logging
import sys
import traceback

LOG_LIMIT = 1000
global_logs = deque(maxlen=LOG_LIMIT)

def create_exchook(file=sys.stderr, max_lines_per_function=25):

    def exchook(etype, value, tb):

        def _create_log_lines(logs):
            log_msg = '\n    logs:\n'
            for pos, (log_record, log_handler) in enumerate(logs):
                log_msg += ' ' * 8
                log_msg += 'line %d, msg: %s' % (log_record.lineno, log_handler.format(log_record))
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
            (filename, lineno, fn_name, line) = _extract_traceback(tb)

            logs = [(record, handler) for (record, handler) in global_logs
                if record.funcName == fn_name and record.pathname == filename]
            logs = logs[-max_lines_per_function:]
            if len(logs) > 0:
                line += _create_log_lines(logs)

            list.append((filename, lineno, fn_name, line))
            tb = tb.tb_next
            n = n+1

        file.write('Traceback (most recent call last):\n')
        map(file.write, traceback.format_list(list))
        map(file.write, traceback.format_exception_only(etype, value))
        global_logs.clear()

    return exchook


class LogCollector(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            global global_logs
            global_logs.append((record, self))
        except:
            self.handleError(record)
