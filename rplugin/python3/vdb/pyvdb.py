class CallBacks:
    def __init__(self, vdb):
        self.vdb_ = vdb

    def on_attached(self):
        pass

    def output(self, msg: bytes):
        self.vdb_.dbg_win_.output(msg)


dbgs = {}
class DBG:
    def __init__(self):
        self.cbs_ = None

    def set_cbs(self, cbs):
        self.cbs_ = cbs

    def start(self):
        pass

    def execute(self, cmd: str):
        pass


def register_dbg(name: str, dbg: DBG):
    global dbgs
    dbgs[name] = dbg

class VDBEventHandler:
    def __init__(self) -> None:
        pass

