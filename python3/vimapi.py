import vim

def win_getid():
    return int(vim.eval('win_getid()'))

def execute(cmd: str):
    vim.command("execute '%s'" % cmd)

def bufnr():
    return int(vim.eval('bufnr()'))

def call(func: str):
    vim.command("call %s" % func)

def eval(what: str):
    return vim.eval(what)

def win_id2win(id: int) -> int:
    return int(vim.eval('win_id2win(%d)' % id))

def bufadd(name: str):
    return int(eval("bufadd('%s')" % name))

def win_execute(win_id: int, cmd: str):
    call("win_execute(%d, '%s')" % (win_id, cmd))

def bufexists(buf) -> bool:
    return bool(vim.eval("bufexists(" + str(buf) + ")"))

def win_gotoid(id):
    call("win_gotoid(" + str(id) +  ")")

def winwidth(nr):
    return int(eval("winwidth('%d')" % nr))

def getbufinfo(nr):
    infos = vim.eval("getbufinfo()")
    for info in infos:
        if info['bufnr'] == str(nr):
            return info

## if val is a str: no, pass in as 'no', add a quote to it
## if val is a number, pass in as a str
def setbuflocal(winid: int, bufnr: int, opt: str, val: str):
    call("nvim_set_option_value('%s', %s, \
         {'scope': 'local',\
         'win': %d},\
         'buf': %d)" % (opt, val, winid, bufnr))