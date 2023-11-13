import logging

_logger = None

def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = init_logging()
    return _logger

def init_logging(log_file: str = '/tmp/vdb.log', log_level = logging.DEBUG):
    global _logger
    logger_handler = logging.FileHandler(log_file)
    logger_formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    logger_formatter.datefmt = '%Y/%m/%d %I:%M:%S %p'
    logger_handler.setFormatter(logger_formatter)
    _logger = logging.getLogger('vdb')
    _logger.setLevel(log_level)
    _logger.addHandler(logger_handler)
    return _logger

