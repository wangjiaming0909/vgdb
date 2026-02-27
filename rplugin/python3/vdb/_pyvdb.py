class CallBacks:
    def __init__(self, vdb):
        self.vdb_ = vdb

    def on_attached(self):
        pass

    def output(self, msg: bytes):
        self.vdb_.dbg_win_.output(msg)

class DBG:
    def __init__(self):
        self.cbs_ = None
        self.start_command_ = []
        self.channel_id_ = -1
        self.nvim_ = None

    def set_channel_id(self, id: int):
        self.channel_id_ = id

    def set_cbs(self, cbs):
        self.cbs_ = cbs

    def get_cbs(self):
        if self.cbs_ is not None:
            return self.cbs_
        return None

    def get_start_command(self):
        return self.start_command_
    
    def set_nvim(self, nvim):
        self.nvim_ = nvim

    def start(self):
        pass

    def execute(self, cmd: str):
        pass

class VDBEventHandler:
    def __init__(self) -> None:
        pass

_dbgs = {}
def register_dbg(name: str, dbg: DBG):
    global _dbgs
    _dbgs[name] = dbg

def get_dbgs():
    global _dbgs
    return _dbgs
