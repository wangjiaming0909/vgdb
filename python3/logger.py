import logging
logger = None

def init_logging(log_file: str = '/tmp/vdb.log', log_level = logging.DEBUG):
    global logger
    logger_handler = logging.FileHandler(log_file)
    logger_formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    logger_formatter.datefmt = '%Y/%m/%d %I:%M:%S %p'
    logger_handler.setFormatter(logger_formatter)
    logger = logging.getLogger('vdb')
    logger.setLevel(log_level)
    logger.addHandler(logger_handler)

