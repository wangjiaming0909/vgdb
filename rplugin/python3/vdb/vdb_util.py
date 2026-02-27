from .logger import get_logger

def assert_fail(msg):
    get_logger().error(msg)
    print(msg)

def vdb_assert(expr: bool, msg: str):
    if not expr:
        get_logger().error(msg)
        print(msg)
        exit(0)
