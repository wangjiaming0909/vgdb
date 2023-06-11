import pynvim
import uuid
from enum import Enum
from queue import Queue
from typing import Dict, List
from pygdbmi.gdbcontroller import GdbController
from pygdbmi.IoManager import IoManager
from pynvim.api import Buffer
from pynvim.api import Window

def is_last_line(vim_ins: pynvim.Nvim):
    return vim_ins.eval("getpos('.')[1] == line('$')")

class GDBCommand:
    def __init__(self, cmd: str):
        self.cmd = cmd
        self.id = uuid.uuid4()
        pass
    def get_mi_cmd(self) -> str:
        return self.cmd

class GDBOutPutMsgType(Enum):
    NOTIFY = 1
    LOG = 2
    CONSOLE = 3
    RESULT = 4

class GDBOutputManager:
    def __init__(self):
        self.notify_msgs: dict[uuid.UUID, dict]= {}
        self.log_msgs: dict[uuid.UUID, dict] = {}
        self.console_msgs: dict[uuid.UUID, dict] = {}
        self.result_msgs: dict[uuid.UUID, dict] = {}
        self.msgs: dict[GDBOutPutMsgType, dict[uuid.UUID, dict]] = {}
        self.max_size = 100
        self.msg_num = 0
        self.msg_queue: Queue[uuid.UUID] = Queue()

    def check_and_resize_msgs(self, put_id: uuid.UUID):
        if self.msg_queue.qsize() > self.max_size:
            id = self.msg_queue.get()
            msgs:dict[uuid.UUID, dict]|None = self.msgs.get(GDBOutPutMsgType.NOTIFY)
            if msgs is not None:
                msgs.pop(id)
        self.msg_queue.put(put_id)

    def add_msg(self, msg_type: GDBOutPutMsgType, id: uuid.UUID, msg: dict):
        self.check_and_resize_msgs(id)
        if msg_type not in self.msgs:
            self.msgs[msg_type] = {}
        self.msgs[msg_type][id] = msg

    def get_msg(self, msg_type: GDBOutPutMsgType, id: uuid.UUID) -> dict:
        if msg_type in self.msgs:
            if id in self.msgs[msg_type]:
                return self.msgs[msg_type][id]
        return None

output_manager = GDBOutputManager()

class GDBOutput:
    def __init__(self, cmd: GDBCommand, mi_msg: List):
        msg: dict = {}
        self.mi_msg: List = mi_msg
        self.cmd = cmd
        self.id = cmd.id
        for msg in self.mi_msg:
            type_v = msg.get("type")
            if type_v is None:
                continue
            if type_v == "notify":
                output_manager.add_msg(GDBOutPutMsgType.NOTIFY, cmd.id, msg)
            elif type_v == "log":
                output_manager.add_msg(GDBOutPutMsgType.LOG, cmd.id, msg)
            elif type_v == "console":
                output_manager.add_msg(GDBOutPutMsgType.CONSOLE, cmd.id, msg)
            elif type_v == "result":
                output_manager.add_msg(GDBOutPutMsgType.RESULT, cmd.id, msg)

    def get_msg(self):
        msg:dict = {}
        log:str = output_manager.get_msg(GDBOutPutMsgType.LOG, self.cmd.id).get("payload")
        return log[:-1] + " -> " + output_manager.get_msg(GDBOutPutMsgType.CONSOLE, self.cmd.id).get("payload")

    def get_console_msg(self):
        return output_manager.get_msg(GDBOutPutMsgType.CONSOLE, self.cmd.id)

    def get_total_msg(self):
        return self.mi_msg

class GDBInstance:
    def __init__(self) -> None:
        self.gdb_controller: GdbController = None

    def start(self):
        self.gdb_controller = GdbController()

    def exit(self):
        self.gdb_controller.exit()

    def execute_str(self, cmd: str):
        return self.execute(GetPrintCmd(cmd))

    def execute(self, cmd: GDBCommand) -> str:
        ret = self.gdb_controller.write(cmd.get_mi_cmd())
        return GDBOutput(cmd, ret).get_msg()

    def ExecuteAsync(self, cmd: GDBCommand, callback):
        pass

def GetPrintCmd(c: str) ->GDBCommand:
    cmd = GDBCommand(c)
    return cmd

def GetStepCmd() ->GDBCommand:
    pass

def GetNextCmd() ->GDBCommand:
    pass

def GetFinCmd() -> GDBCommand:
    pass

def GetSetBreakPointCmd(file: str, line_nu: int) ->GDBCommand:
    pass

def GetDisableBreakPointCmd(file: str, line_nu: int) ->GDBCommand:
    pass

def GetDeleteBreakPointCmd(file: str, line_nu:int) ->GDBCommand:
    pass

def GetContinueCmd() ->GDBCommand:
    pass

def GetStackUpCmd() ->GDBCommand:
    pass

def GetStackDownCmd() ->GDBCommand:
    pass

def GetFrameCmd() ->GDBCommand:
    pass

def GetInfoLocalsCmd() ->GDBCommand:
    pass

def GetInfoBreaksCmd() ->GDBCommand:
    pass

def GetInfoThreadsCmd() ->GDBCommand:
    pass

def GetThreadCmd() ->GDBCommand:
    pass

def GetSaveBreaksCmd() ->GDBCommand:
    pass

def GetSourceBreaksCmd() ->GDBCommand:
    pass

class GDBWinInstance:
    def __init__(self, nvim_instance: pynvim.Nvim):
        #self.pwd = os.path.abspath(os.path.curdir)
        self.nvim_instance = nvim_instance
        self.last_win: Window = None
        self.last_win_id = -1
        self.gdb_window: Window = None
        self.gdb_win_id = -1
        self.gdb_output_file = '/tmp/gdb_console'
        self.gdb_prompt = '(gdb)'

    # add prompt to gdb_window
    def setup_prompt(self):
        buf: Buffer = self.gdb_window.buffer
        buf.append(self.gdb_prompt + ' ')

    def create_gdb_win(self):
        with open(self.gdb_output_file, 'w+') as f:
            f.truncate(0)
            f.write('-------Hello TO VGDB-------')
        self.nvim_instance.command('vertical topleft 40 split {}'.format(self.gdb_output_file))
        self.gdb_window = self.nvim_instance.current.window
        self.gdb_win_id = self.nvim_instance.eval('win_getid()')

    def go_to_gdb_win(self):
        cur_win_id = self.nvim_instance.eval('win_getid()')
        if self.gdb_win_id == cur_win_id:
            return
        else:
            self.last_win_id = cur_win_id
        self.nvim_instance.call('win_gotoid', self.gdb_win_id)

    # should only be called after go_to_gdb_win
    def pre_command(self):
        self.nvim_instance.feedkeys("GA", 'm', escape_csi=True)

    def init_gdb_win(self):
        self.setup_prompt()
        self.nvim_instance.feedkeys('GA')
        self.nvim_instance.command('nnoremap <buffer> i GA')
        self.nvim_instance.command('nnoremap <buffer> a GA')
        self.nvim_instance.command('nnoremap <buffer> o GA')
        self.nvim_instance.command('nnoremap <buffer> I GA')
        self.nvim_instance.command('nnoremap <buffer> A GA')
        self.nvim_instance.command('nnoremap <buffer> O GA')
        self.nvim_instance.command('inoremap <buffer> <BS> ')

    # new gdb_window
    def start(self):
        self.create_gdb_win()
        self.init_gdb_win()

    def is_modifiable(self):
        if not is_last_line(self.nvim_instance):
            return False
        # last line
        cur_line: str = self.nvim_instance.current.line
        if cur_line.startswith(self.gdb_prompt):
            col_n = self.nvim_instance.eval("col('.')")
        return True

    def hide(self):
        pass

    def exit(self):
        pass

    def execute(self):
        pass

    # go to the gdb window
    def enter_gdb_win(self):
        self.go_to_gdb_win()

    # leave the gdb window, get back to the original window
    def leave_gdb_win(self):
        self.nvim_instance.call('win_gotoid', self.last_win_id)

class VGDBManager:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        self.gdb_mi: GDBInstance = GDBInstance()
        self.gdb_win: GDBWinInstance = GDBWinInstance(nvim)

    def start(self):
        self.gdb_mi.start()
        #self.gdb_win.start()

    def exit(self):
        self.gdb_mi.exit()
        #self.gdb_win.exit()

    def execute(self, cmd: str):
        return self.gdb_mi.execute_str(cmd)

    def hide(self):
        self.gdb_win.hide()

    def go_to_gdb_win(self):
        self.gdb_win.go_to_gdb_win()

@pynvim.plugin
class VGDB(object):
    def __init__(self, vim: pynvim.Nvim):
        self.vim = vim
        self.vgdb_manager = VGDBManager(self.vim)

    @pynvim.function('GDBStart')
    def start_gdb(self, arg):
        self.vgdb_manager.start()

    @pynvim.function('GDBStop')
    def stop_gdb(self, arg):
        self.vgdb_manager.exit()

    @pynvim.function('GDBExecute')
    def execute(self, arg):
        return self.vgdb_manager.execute(arg)

