from .vdb_gdb import register_gdb
from .vdb_lldb import register_lldb
from ._pyvdb import CallBacks, DBG, get_dbgs as get_raw_dbgs

def _register_all_dbgs():
    register_gdb()
    register_lldb()

def get_dbgs():
    if len(get_raw_dbgs()) == 0:
        _register_all_dbgs()
    return get_raw_dbgs()
