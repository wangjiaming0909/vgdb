from vdb import configs
from vdb import logger
from vdb import vdb_util
from vdb import vimapi

class VDBWin:
    def __init__(self, nvim) -> None:
        self.nvim_ = nvim
        if logger.get_logger() is None:
            raise Exception("logger not inited")
        self.buf_file_ = '/tmp/.vdb_console'
        if configs.has_config('dbg_win_width'):
            self.win_width_ = int(configs.get_config('dbg_win_width'))
        else:
            self.win_width_ = 40
        self.original_win_id_ = None
        self.dbg_win_id_ = None
        self.dbg_buf_nr_ = None

    def setup_dbg_win(self):
        def set_dbg_buf_local_opt(opt: str, val):
            if self.dbg_buf_nr_ is not None:
                vimapi.setbuflocal(self.nvim_, self.dbg_buf_nr_, opt, val)
        def set_dbg_win_local_opt(opt: str, val):
            if self.dbg_win_id_ is not None:
                vimapi.setwinlocal(self.nvim_, self.dbg_win_id_, opt, val)
        set_dbg_win_local_opt('signcolumn', 'no')
        set_dbg_win_local_opt('scrolloff', 1)
        set_dbg_win_local_opt('nu', False)
        set_dbg_buf_local_opt('syntax', 'vgdb')
        set_dbg_buf_local_opt('bh', 'hide')
        set_dbg_buf_local_opt('buftype', 'prompt')
        set_dbg_win_local_opt('statusline', '%<%F[%1*%M%*%n%R%H]')
        vimapi.execute(self.nvim_, "autocmd BufModifiedSet <buffer=%d> set nomodified" % self.dbg_buf_nr_)
        vimapi.execute(self.nvim_, "autocmd InsertCharPre <buffer=%d> python3 import vdb_win" % self.dbg_buf_nr_)

    def create(self):
        if self.dbg_win_id_ is not None:
            print('DBG win already created')
            return
        self.original_win_id_ = vimapi.win_getid(self.nvim_)
        logger.get_logger().debug('original win id: %d' % self.original_win_id_)
        vimapi.execute(self.nvim_, "vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
        # now we are in the dbg_win
        self.dbg_win_id_ = vimapi.win_getid(self.nvim_)
        logger.get_logger().debug('dbg win id: %d' % self.dbg_win_id_)
        self.dbg_buf_nr_ = vimapi.bufnr(self.nvim_)
        self.setup_dbg_win()
        vimapi.call(self.nvim_, "cursor('$', 999)")
        # get back to the original win
        vimapi.win_gotoid(self.nvim_, self.original_win_id_)

    def show(self):
        if self.dbg_buf_nr_ is None or not vimapi.bufexists(self.nvim_, self.dbg_buf_nr_):
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.nvim_, self.dbg_win_id_) == 0:
                logger.get_logger().debug('start to create dbg win')
                self.create()
            else:
                logger.get_logger().debug('start to load dbg buf')
                self.dbg_buf_nr_ = vimapi.bufadd(self.nvim_, self.buf_file_)
                vimapi.win_execute(self.nvim_, self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr_)
        else:
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.nvim_, self.dbg_win_id_) == 0:
                logger.get_logger().debug('start to create dbg win and load buf')
                self.dbg_buf_nr_ = vimapi.bufadd(self.nvim_, self.buf_file_)
                vimapi.execute(self.nvim_, "vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
                self.dbg_win_id_ = vimapi.win_getid(self.nvim_)
            else:
                logger.get_logger().debug('start to load dbg buf %d', self.dbg_win_id_)
                vimapi.win_execute(self.nvim_, self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr_)
        # go back to original win id
        if self.original_win_id_ is not None and vimapi.win_id2win(self.nvim_, self.original_win_id_) != 0:
            vimapi.win_gotoid(self.nvim_, self.original_win_id_)

    def hide(self):
        if self.dbg_win_id_ is not None and 0 != vimapi.win_id2win(self.nvim_, self.dbg_win_id_):
            vimapi.win_gotoid(self.nvim_,self.dbg_win_id_)
            self.win_width_ = vimapi.winwidth(self.nvim_, 0)
            vimapi.execute(self.nvim_, 'hide')

    def output(self, msg: bytes):
        if self.dbg_buf_nr_ is not None:
            vimapi.appendbufline(self.nvim_, self.dbg_buf_nr_, str(msg))



_vdb_win = None

def get_vdb_win() -> VDBWin:
    global _vdb_win
    if _vdb_win is None:
        _vdb_win = VDBWin()
        _vdb_win.create()
    return _vdb_win

def Test_dbg_win():
    vdb_win = get_vdb_win()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert go back to original win failed, cur win_id: %d, original_win_id: %d" % (vimapi.win_getid(), vdb_win.original_win_id_)
        vdb_util.assert_fail(msg)
        return
    vimapi.win_gotoid(vdb_win.dbg_win_id_)
    if vdb_win.dbg_win_id_ != vimapi.win_getid():
        msg = "assert in dbg win id failed, cur win id: %d, dbg_win_id: %d" % (vimapi.win_getid(), vdb_win.dbg_win_id_)
        vdb_util.assert_fail(msg)
        return
    vdb_win.hide()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert go back to original win failed, cur win_id: %d, original_win_id: %d" % (vimapi.win_getid(), vdb_win.original_win_id_)
        vdb_util.assert_fail(msg)
        return
    dbg_buf_info = vimapi.getbufinfo(vdb_win.dbg_buf_nr_)
    logger.get_logger().debug(str(dbg_buf_info))
    if dbg_buf_info['hidden'] != '1':
        msg = "assert dbg win buffer hidden failed bufnr: %d, v: %s" % (vdb_win.dbg_buf_nr_, str(dbg_buf_info['hidden']))
        vdb_util.assert_fail(msg)
        return
    vdb_win.show()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert in original win id failed, cur win id: %d, dbg_win_id: %d" % (vimapi.win_getid(), vdb_win.dbg_win_id_)
        vdb_util.assert_fail(msg)
        return
    dbg_buf_info = vimapi.getbufinfo(vdb_win.dbg_buf_nr_)
    logger.get_logger().debug(str(dbg_buf_info))
    vdb_util.vdb_assert(dbg_buf_info['hidden'] == '0', 'assert vdb buf showed failed')
