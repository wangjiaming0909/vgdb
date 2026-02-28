import pynvim
from .vdb_dbg import get_dbgs,CallBacks, DBG
from .logger import get_logger
from .vdb_win import VDBWin
from .configs import get_config, configs

@pynvim.plugin
class VDB(object):
    def __init__(self, nvim):
        self.nvim_ = nvim
        self.dbg_name_ = None
        try:
            self.dbg_name_ = get_config('dbg')
        except Exception as e:
            get_logger().error( \
                    'failed to get dbg from config: %s, e: %s' % \
                    (configs, str(e)))
            print('get dbg from config failed')
            raise
        self.dbg_: DBG = get_dbgs()[self.dbg_name_]
        self.cbs_ = CallBacks(self)
        self.dbg_.set_cbs(self.cbs_)
        self.dbg_win_ = VDBWin(nvim, self.dbg_)
        self.dbg_.set_nvim(nvim)

    @pynvim.command('VDBStart')
    def start(self):
        self.dbg_win_.create()
        self.dbg_.start()
        self.dbg_win_.show()
    
    @pynvim.function("DBGWinTextEntered")

    def stop(self):
        pass

    def execute(self, cmd: str):
        self.dbg_.execute(cmd)
