from logger import logger

def assert_fail(msg):
    logger.error(msg)
    print(msg)

def vdb_assert(expr: bool, msg: str):
    if not expr:
        logger.error(msg)
        print(msg)
        exit(0)
