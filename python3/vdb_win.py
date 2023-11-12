import configs
from logger import logger
from util import *

class VDBWin:
    def __init__(self) -> None:
        self.buf_file_ = '/tmp/.vdb_console'
        if configs.has_config('dbg_win_width'):
            self.win_width_ = int(configs.get_config('dbg_win_width'))
        else:
            self.win_width_ = 40
        self.original_win_id_ = None
        self.dbg_win_id_ = None
        self.dbg_buf_nr = None
    
    def setup_dbg_win(self):
        import vimapi
        def set_dbg_buf_local_opt(opt: str, val):
            vimapi.setbuflocal(self.dbg_buf_nr, opt, val)
        def set_dbg_win_local_opt(opt: str, val):
            vimapi.setwinlocal(self.dbg_win_id_, opt, val)
        set_dbg_win_local_opt('signcolumn', 'no')
        set_dbg_win_local_opt('scrolloff', 1)
        set_dbg_win_local_opt('nu', False)
        set_dbg_buf_local_opt('syntax', 'vgdb')
        set_dbg_buf_local_opt('bh', 'hide')
        set_dbg_buf_local_opt('buftype', 'prompt')
        set_dbg_win_local_opt('statusline', '%<%F[%1*%M%*%n%R%H]')
        vimapi.execute("autocmd BufModifiedSet <buffer=%d> set nomodified" % self.dbg_buf_nr)

    def create(self):
        import vimapi
        if self.dbg_win_id_ is not None:
            print('DBG win already created')
            return
        self.original_win_id_ = vimapi.win_getid()
        logger.debug('original win id: %d' % self.original_win_id_)
        vimapi.execute("vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
        # now we are in the dbg_win
        self.dbg_win_id_ = vimapi.win_getid()
        logger.debug('dbg win id: %d' % self.dbg_win_id_)
        self.dbg_buf_nr = vimapi.bufnr()
        self.setup_dbg_win()
        vimapi.call("cursor('$', 999)")
        # get back to the original win
        vimapi.call("win_gotoid(%d)" % self.original_win_id_)
    
    def show(self):
        import vimapi
        if self.dbg_buf_nr is None or not vimapi.bufexists(self.dbg_buf_nr):
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.dbg_win_id_) == 0:
                logger.debug('start to create dbg win')
                self.create()
            else:
                logger.debug('start to load dbg buf')
                self.dbg_buf_nr = vimapi.bufadd(self.buf_file_)
                vimapi.win_execute(self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr)
        else:
            if self.dbg_win_id_ is None or vimapi.win_id2win(self.dbg_win_id_) == 0:
                logger.debug('start to create dbg win and load buf')
                self.dbg_buf_nr = vimapi.bufadd(self.buf_file_)
                vimapi.execute("vertical topleft %d split %s" % (self.win_width_, self.buf_file_))
                self.dbg_win_id_ = vimapi.win_getid()
            else:
                logger.debug('start to load dbg buf %d', self.dbg_win_id_)
                vimapi.win_execute(self.dbg_win_id_, 'call bufload(%d)' % self.dbg_buf_nr)
        # go back to original win id
        if self.original_win_id_ is not None and vimapi.win_id2win(self.original_win_id_) != 0:
            vimapi.win_gotoid(self.original_win_id_)
    
    def hide(self):
        import vimapi
        if self.dbg_win_id_ is not None and 0 != vimapi.win_id2win(self.dbg_win_id_):
            vimapi.win_gotoid(self.dbg_win_id_)
            self.win_width_ = vimapi.winwidth(0)
            vimapi.execute('hide')
    
vdb_win: VDBWin = None

def Test_dbg_win():
    import vimapi
    global vdb_win
    vdb_win = VDBWin()
    vdb_win.create()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert go back to original win failed, cur win_id: %d, original_win_id: %d" % (vimapi.win_getid(), vdb_win.original_win_id_)
        assert_fail(msg)
        return
    vimapi.win_gotoid(vdb_win.dbg_win_id_)
    if vdb_win.dbg_win_id_ != vimapi.win_getid():
        msg = "assert in dbg win id failed, cur win id: %d, dbg_win_id: %d" % (vimapi.win_getid(), vdb_win.dbg_win_id_)
        assert_fail(msg)
        return
    vdb_win.hide()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert go back to original win failed, cur win_id: %d, original_win_id: %d" % (vimapi.win_getid(), vdb_win.original_win_id_)
        assert_fail(msg)
        return
    dbg_buf_info = vimapi.getbufinfo(vdb_win.dbg_buf_nr)
    logger.debug(str(dbg_buf_info))
    if dbg_buf_info['hidden'] != '1':
        msg = "assert dbg win buffer hidden failed bufnr: %d, v: %s" % (vdb_win.dbg_buf_nr, str(dbg_buf_info['hidden']))
        assert_fail(msg)
        return
    vdb_win.show()
    if vdb_win.original_win_id_ != vimapi.win_getid():
        msg = "assert in original win id failed, cur win id: %d, dbg_win_id: %d" % (vimapi.win_getid(), vdb_win.dbg_win_id_)
        assert_fail(msg)
        return
    dbg_buf_info = vimapi.getbufinfo(vdb_win.dbg_buf_nr)
    logger.debug(str(dbg_buf_info))
    vdb_assert(dbg_buf_info['hidden'] == '0', 'assert vdb buf showed failed')
