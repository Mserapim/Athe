import json
import logging
import socket
import traceback


class GELFFormatter(logging.Formatter):
    def format(self, record):
        timestamp = record.created
        full_message = ""

        if record.exc_info:
            full_message = "".join(traceback.format_exception(*record.exc_info))
        elif record.exc_text:
            full_message = record.exc_text

        log_entry = {
            "version": "1.1",
            "file": record.pathname,
            "line": record.lineno,
            "_pid": record.process,
            "_thread_name": record.threadName,
            "host": socket.gethostname(),
            "short_message": record.getMessage(),
            "full_message": full_message,
            "timestamp": timestamp,
            "level": record.levelno,
            "hostname": record.hostname,
            "process_name": record.processName,
            "remote_addr": record.remote_addr,
            "req_method": record.req_method,
            "req_path": record.req_path,
            "stream_name": record.stream_name,
            "user": record.user,
            "_logger_name": record.name,
            "_module": record.module,
            "_function": record.funcName,
            "facility": "base-athenas",
        }
        return json.dumps(log_entry)


class GELFUDPHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def emit(self, record):
        try:
            message = self.format(record)
            self.socket.sendto(message.encode("utf-8"), self.address)
        except Exception:
            self.handleError(record)
