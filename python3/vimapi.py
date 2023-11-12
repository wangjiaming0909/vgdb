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

def setwinlocal(winid: int, opt: str, val = None):
    if val is not None:
        if type(val) is int:
            call("nvim_set_option_value('%s', %d, {'win': %d})" % (opt, val, winid))
        elif type(val) is str:
            call("nvim_set_option_value('%s', '%s', {'win': %d})" % (opt, val, winid))
        elif type(val) is bool:
            if val:
                bool_val = 'v:true'
            else:
                bool_val = 'v:false'
            call("nvim_set_option_value('%s', %s, {'win': %d})" % (opt, bool_val, winid))

## if val is a str: no, pass in as 'no', add a quote to it
## if val is a number, pass in as a str
def setbuflocal(bufnr: int, opt: str, val = None):
    if val is not None:
        if type(val) is int:
            call("nvim_set_option_value('%s', %d, {'buf': %d})" % (opt, val, bufnr))
        elif type(val) is str:
            call("nvim_set_option_value('%s', '%s', {'buf': %d})" % (opt, val, bufnr))
        elif type(val) is bool:
            if val:
                bool_val = 'v:true'
            else:
                bool_val = 'v:false'
            call("nvim_set_option_value('%s', %s, {'buf': %d})" % (opt, bool_val, bufnr))