from .configs import has_config,get_config
from .logger import get_logger
from .vdb_util import assert_fail, vdb_assert
from . import vimapi
import pynvim
from ._pyvdb import DBG

class VDBWin:
    def __init__(self, nvim: pynvim.Nvim, dbg: DBG) -> None:
        self.nvim_ = nvim
        if get_logger() is None:
            raise Exception("logger not inited")
        self.buf_file_ = '/tmp/.vdb_console'
        if has_config('dbg_win_width'):
            self.win_width_ = int(get_config('dbg_win_width'))
        else:
            self.win_width_ = 40
        self.original_win_id_ = None
        self.dbg_win_id_ = None
        self.dbg_buf_nr_ = None
        self.in_command_ = False
        self.command_got_output = False
        self.dbg_ = dbg
        self.channel_id_: int = -1

    def setup_dbg_win(self):
        def set_dbg_buf_local_opt(opt: str, val):
            if self.dbg_buf_nr_ is not None:
                vimapi.setbuflocal(self.nvim_, self.dbg_buf_nr_, opt, val)
        def set_dbg_win_local_opt(opt: str, val):
            if self.dbg_win_id_ is not None:
                vimapi.setwinlocal(self.nvim_, self.dbg_win_id_, opt, val)
        #set_dbg_win_local_opt('signcolumn', 'no')
        #set_dbg_win_local_opt('scrolloff', 1)
        #set_dbg_win_local_opt('nu', False)
        #set_dbg_buf_local_opt('syntax', 'vgdb')
        #set_dbg_buf_local_opt('bh', 'hide')
        #set_dbg_buf_local_opt('buftype', 'prompt')
        #set_dbg_win_local_opt('statusline', '%<%F[%1*%M%*%n%R%H]')
        #vimapi.execute(self.nvim_, "autocmd BufModifiedSet <buffer=%d> set nomodified" % self.dbg_buf_nr_)
        #vimapi.execute(self.nvim_, "autocmd InsertCharPre <buffer=%d> exec \"VDBBufCharCB\" v:char" % self.dbg_buf_nr_)
        #vimapi.call(self.nvim_, 'VDBBufEnterCB("internal")')
        #vimapi.call(self.nvim_, "prompt_setcallback(%d, 'VDBBufEnterCB')" % self.dbg_buf_nr_)

    def vdb_buf_char_pre_cb(self):
        pass

    def create(self):
        if self.dbg_win_id_ is not None:
            print('DBG win already created')
            return
        self.original_win_id_ = vimapi.win_getid(self.nvim_)
        get_logger().debug('original win id: %d' % self.original_win_id_)
        vimapi.execute(self.nvim_, "vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
        # now we are in the dbg_win
        self.dbg_win_id_ = vimapi.win_getid(self.nvim_)
        get_logger().debug('dbg win id: %d' % self.dbg_win_id_)
        self.dbg_buf_nr_ = vimapi.bufnr(self.nvim_)
        self.channel_id_ = vimapi.eval(self.nvim_, 'jobstart(%s, {"term":v:true})' % self.dbg_.get_start_command())
        self.dbg_.set_channel_id(self.channel_id_)
        #self.setup_dbg_win()
        #vimapi.call(self.nvim_, "cursor('$', 999)")
        # get back to the original win
        vimapi.win_gotoid(self.nvim_, self.original_win_id_)

    def show(self):
        if self.dbg_buf_nr_ is None or not vimapi.bufexists(self.nvim_, self.dbg_buf_nr_):
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.nvim_, self.dbg_win_id_) == 0:
                get_logger().debug('start to create dbg win')
                self.create()
            else:
                get_logger().debug('start to load dbg buf')
                self.dbg_buf_nr_ = vimapi.bufadd(self.nvim_, self.buf_file_)
                vimapi.win_execute(self.nvim_, self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr_)
        else:
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.nvim_, self.dbg_win_id_) == 0:
                get_logger().debug('start to create dbg win and load buf')
                self.dbg_buf_nr_ = vimapi.bufadd(self.nvim_, self.buf_file_)
                vimapi.execute(self.nvim_, "vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
                self.dbg_win_id_ = vimapi.win_getid(self.nvim_)
            else:
                get_logger().debug('start to load dbg buf %d', self.dbg_win_id_)
                vimapi.win_execute(self.nvim_, self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr_)
        # go back to original win id
        if self.original_win_id_ is not None and vimapi.win_id2win(self.nvim_, self.original_win_id_) != 0:
            vimapi.win_gotoid(self.nvim_, self.original_win_id_)

    def hide(self):
        if self.dbg_win_id_ is not None and 0 != vimapi.win_id2win(self.nvim_, self.dbg_win_id_):
            vimapi.win_gotoid(self.nvim_,self.dbg_win_id_)
            self.win_width_ = vimapi.winwidth(self.nvim_, 0)
            vimapi.execute(self.nvim_, 'hide')

    def do_output(self, msg):
        line_offset: int = 0
        if self.in_command_:
            line_offset = -1
        vimapi.appendbufline(self.nvim_, self.dbg_buf_nr_, msg, line_offset)

    def output(self, msg: bytes):
        if self.dbg_buf_nr_ is not None:
            self.nvim_.async_call(self.do_output, msg)