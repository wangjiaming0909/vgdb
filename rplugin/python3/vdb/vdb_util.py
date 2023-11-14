from vdb.logger import _logger

def assert_fail(msg):
    _logger.error(msg)
    print(msg)

def vdb_assert(expr: bool, msg: str):
    if not expr:
        _logger.error(msg)
        print(msg)
        exit(0)
