from ._pyvdb import DBG,register_dbg

class LLDB(DBG):
    def __init__(self):
        super().__init__()
        self.start_command_ = ['lldb']

def register_lldb():
    register_dbg("lldb", LLDB())
