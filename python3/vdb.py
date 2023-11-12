import configs
from logger import logger
from vdb_win import VDBWin

class DBG:
    def __init__(self):
        self.cbs_ = None
    
    def set_cbs(self, cbs):
        self.cbs_ = cbs

    def start(self):
        pass

    def execute(self):
        pass

dbgs = {}

def register_dbg(name: str, dbg: DBG):
    global dbgs
    if name in dbgs:
        raise Exception('already registered')
    dbgs[name] = dbg

class VDBEventHandler:
    def __init__(self) -> None:
        pass

class VDB:
    def __init__(self):
        self.dbg_win_ = VDBWin()
        self.dbg_name_ = configs.get_config('dbg')
        self.dbg_: DBG = dbgs[self.dbg_name_]
        self.cbs_ = CallBacks(self)
        self.dbg_.set_cbs(self.cbs_)

    def start(self):
        self.dbg_.start()
        self.dbg_win_.create()
        self.dbg_win_.show()

    def stop(self):
        pass

    def execute(self, cmd: str):
        self.dbg_.execute(cmd)

class CallBacks:
    def __init__(self, vdb: VDB):
        self.vdb_ = vdb
    def on_attached(self):
        pass

if __name__ == '__main__':
    import os
    master,slave = os.openpty()
    from ctypes import *
    libc = cdll.LoadLibrary('libc.so.6')
    libc.grantpy(master)
    libc.unlockpt(master)
    print(os.ttyname(slave))
    #Test_dbg_win()
    #gdb = GDB()
    #gdb.start()
    #time.sleep(500)