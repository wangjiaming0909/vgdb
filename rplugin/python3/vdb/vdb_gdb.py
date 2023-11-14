import select, os, threading, time, subprocess
from . import logger
from . import pyvdb

class GDB(pyvdb.DBG):
    def __init__(self):
        super().__init__()
        self.p_ = None
        self.args_ = ['gdb']
        self.epoller_ = select.epoll()
        self.mi_epoller_ = select.epoll()
        self.output_handler_ = threading.Thread(target=GDB.handle_output, args=[self])
        self.exit_ = False
        self.pty_master_fd_ = None
        self.pty_slave_fd_ = None
        self.slave_pty_name_ = None
        self.output_handler_running_ = False
        self.mi_output_handler_ = threading.Thread(target=GDB.handle_mi_output, args=[self])

    def handle_output(self):
        self.output_handler_running_ = True
        if self.p_ is not None:
            while not self.exit_:
                if self.p_.stdout is None:
                    break
                if not self.p_.stdout.readable():
                    time.sleep(500)
                    continue
                actives = self.epoller_.poll(0.5)
                if len(actives) > 0:
                    data = self.p_.stdout.read()
                    if super().cbs_ is not None:
                        super().cbs_.output(data)
                    logger._logger.debug(self.p_.stdout.read())
                    actives = []
        self.output_handler_running_ = False

    def handle_mi_output(self):
        if self.pty_master_fd_ is None:
            return
        while not self.exit_:
            actives = self.mi_epoller_.poll(0.5)
            if len(actives) > 0:
                logger._logger.debug(os.read(self.pty_master_fd_, 4096))
                actives = []

    def start(self):
        self.p_ = subprocess.Popen(self.args_, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.p_ is None or self.p_.stdout is None or self.p_.stderr is None:
            logger._logger.error('failed to start gdb with cmd: %s' % self.args_)
            raise Exception('start gdb failed, stdout or stderr is None')
        self.epoller_.register(self.p_.stdout.fileno(), select.POLLIN)
        self.epoller_.register(self.p_.stderr.fileno(), select.POLLIN)
        self.pty_master_fd_, self.pty_slave_fd_ = os.openpty()
        self.mi_epoller_.register(self.pty_master_fd_, select.POLLIN)
        self.slave_pty_name_ = os.ttyname(self.pty_slave_fd_)
        self.output_handler_.start()
        self.mi_output_handler_.start()
        if self.output_handler_running_:
            self.execute('new-ui mi %s' % self.slave_pty_name_)

    def execute(self, cmd: str):
        if self.p_ is None or self.p_.stdin is None:
            return
        if self.p_.stdin.writable():
            len = self.p_.stdin.write((cmd+'\n').encode('utf-8'))
            logger._logger.debug("execute with len: %d" % len)
            self.p_.stdin.flush()

    def stop(self):
        self.exit_ = True
        if self.p_ is not None:
            self.p_.terminate()

    def interrupte(self):
        if self.p_ is not None and self.p_.stdin is not None:
            self.p_.stdin.write(b'')

pyvdb.register_dbg('gdb', GDB())


if __name__ == '__main__':
    gdb = GDB()
    gdb.start()
    gdb.execute('file ~/codes/cgdb/build/cgdb/cgdb')
    gdb.execute('b main')
    time.sleep(9999)
