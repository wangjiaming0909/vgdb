import configs
import subprocess
import select
import threading
import time
import logging
import vimapi

logger = None

def assert_fail(msg):
    logger.error(msg)
    print(msg)

def vdb_assert(expr: bool, msg: str):
    if not expr:
        logger.error(msg)
        print(msg)

def init_logging(log_file: str = '/tmp/vdb.log', log_level = logging.DEBUG):
    global logger
    logger_handler = logging.FileHandler(log_file)
    logger_formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    logger_formatter.datefmt = '%Y/%m/%d %I:%M:%S %p'
    logger_handler.setFormatter(logger_formatter)
    logger = logging.getLogger('vdb')
    logger.setLevel(log_level)
    logger.addHandler(logger_handler)

init_logging(log_level=logging.DEBUG)

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

class GDB(DBG):
    def __init__(self):
        DBG.__init__(self)
        self.p_ = None
        self.args_ = ['gdb', '-q', '--interpreter=mi3']
        self.epoller_ = select.epoll()
        self.output_handler_ = threading.Thread(target=GDB.handle_output, args=[self])
        self.exit_ = False
    
    def handle_output(self):
        while not self.exit_:
            if not self.p_.stdout.readable():
                time.sleep(500)
                continue
            actives = self.epoller_.poll(0.5)
            if len(actives) > 0:
                #print(self.p_.stdout.read1())
                actives = []

    def start(self):
        self.p_ = subprocess.Popen(self.args_, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.epoller_.register(self.p_.stdout.fileno(), select.POLLIN)
        self.output_handler_.start()

    def execute(self, cmd: str):
        if self.p_.stdin.writable():
            len = self.p_.stdin.write(cmd)

    def stop(self):
        self.exit_ = True
        if self.p_ is not None:
            self.p_.terminate()

    def interrupte(self):
        if self.p_ is not None:
            self.p_.stdin.write('')

def register_dbg(name: str, dbg: DBG):
    global dbgs
    if name in dbgs:
        raise Exception('already registered')
    dbgs[name] = dbg

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
        pass

    def create(self):
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
        if self.dbg_win_id_ is not None and 0 != vimapi.win_id2win(self.dbg_win_id_):
            vimapi.win_gotoid(self.dbg_win_id_)
            self.win_width_ = vimapi.winwidth(0)
            vimapi.execute('hide')

class VDBEventHandler:
    def __init__(self) -> None:
        pass

class VDB:
    def __init__(self):
        self.dbg_win_ = VDBWin()
        self.dbg_name_ = configs.get_config('dbg')
        register_dbg('gdb', GDB())
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

vdb_win: VDBWin = None

def Test_dbg_win():
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

if __name__ == '__main__':
    Test_dbg_win()
    #gdb = GDB()
    #gdb.start()
    #time.sleep(500)