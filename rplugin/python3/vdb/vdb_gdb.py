import select, os, threading, time, subprocess
from .logger import get_logger
from ._pyvdb import DBG,register_dbg
from . import vimapi
import pynvim

class GDB(DBG):
    def __init__(self):
        super().__init__()
        self.start_command_ = ['gdb']
        self.mi_epoller_ = select.epoll()
        self.exit_ = False
        self.pty_master_fd_ = None
        self.pty_slave_fd_ = None
        self.slave_pty_name_ = None
        self.mi_output_handler_ = threading.Thread(target=GDB.handle_mi_output, args=[self])

    def handle_mi_output(self):
        if self.pty_master_fd_ is None:
            return
        while not self.exit_:
            actives = self.mi_epoller_.poll(0.5)
            if len(actives) > 0:
                get_logger().debug("mi output: %s" % os.read(self.pty_master_fd_, 4096))
                actives = []

    def start(self):
        if self.channel_id_ == -1:
            raise Exception("channel id not initialized")
        get_logger().debug("start gdb with cmd: %s" % self.start_command_)
        self.pty_master_fd_, self.pty_slave_fd_ = os.openpty()
        self.mi_epoller_.register(self.pty_master_fd_, select.POLLIN)
        self.slave_pty_name_ = os.ttyname(self.pty_slave_fd_)

        #self.execute('new-ui mi %s' % self.slave_pty_name_)
        self.execute("new-ui mi %s" % (self.channel_id_, self.slave_pty_name_))
        self.mi_output_handler_.start()

    def execute(self, cmd: str):
        vimapi.call(self.nvim_, 'chansend(%d, "%s\n")' % (self.channel_id_, cmd))

    def stop(self):
        self.exit_ = True

    def interrupte(self):
        pass

def register_gdb():
    register_dbg('gdb', GDB())

if __name__ == '__main__':
    gdb = GDB()
    gdb.start()
    gdb.execute('file ~/codes/cgdb/build/cgdb/cgdb')
    gdb.execute('b main')
    time.sleep(9999)
