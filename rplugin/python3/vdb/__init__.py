import neovim
from . import pyvdb
from . import vdb_win
from . import configs
from . import logger
from . import vdb_gdb

@neovim.plugin
class VDB:
    def __init__(self, nvim: neovim.Nvim):
        self.nvim_ = nvim
        self.dbg_win_ = vdb_win.VDBWin(nvim)
        self.dbg_name_ = None
        try:
            self.dbg_name_ = configs.get_config('dbg')
        except Exception as e:
            logger.get_logger().error( \
                    'failed to get dbg from config: %s, e: %s' % \
                    (configs.configs, str(e)))
            print('get dbg from config failed')
            raise
        self.dbg_: pyvdb.DBG = pyvdb.dbgs[self.dbg_name_]
        self.cbs_ = pyvdb.CallBacks(self)
        self.dbg_.set_cbs(self.cbs_)

    @neovim.command("VDBStart")
    def start(self):
        self.dbg_win_.create()
        self.dbg_win_.show()
        self.dbg_.start()

    def stop(self):
        pass

    def execute(self, cmd: str):
        self.dbg_.execute(cmd)
