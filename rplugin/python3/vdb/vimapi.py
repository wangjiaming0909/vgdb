import neovim

def win_getid(nvim: neovim.Nvim):
    return int(eval(nvim, 'win_getid()'))

def execute(nvim: neovim.Nvim, cmd: str):
    nvim.command("execute '%s'" % cmd)

def bufnr(nvim: neovim.Nvim):
    return int(eval(nvim, 'bufnr()'))

def call(nvim: neovim.Nvim, func: str):
    nvim.command("call %s" % func)

def eval(nvim: neovim.Nvim, what: str):
    return nvim.eval(what)

def win_id2win(nvim: neovim.Nvim, id: int) -> int:
    return int(eval(nvim, 'win_id2win(%d)' % id))

def bufadd(nvim: neovim.Nvim, name: str) ->int:
    return int(eval(nvim, "bufadd('%s')" % name))

def win_execute(nvim: neovim.Nvim, win_id: int, cmd: str):
    call(nvim, "win_execute(%d, '%s')" % (win_id, cmd))

def bufexists(nvim: neovim.Nvim, buf) -> bool:
    return bool(eval(nvim, "bufexists(" + str(buf) + ")"))

def win_gotoid(nvim: neovim.Nvim, id):
    call(nvim, "win_gotoid(" + str(id) +  ")")

def winwidth(nvim, nr):
    return int(eval(nvim, "winwidth('%d')" % nr))

def getbufinfo(nvim,nr):
    infos = eval(nvim, "getbufinfo()")
    for info in infos:
        if info['bufnr'] == str(nr):
            return info
    return {}

def setwinlocal(nvim, winid: int, opt: str, val = None):
    if val is not None:
        if type(val) is int:
            call(nvim, "nvim_set_option_value('%s', %d, {'win': %d})" % (opt, val, winid))
        elif type(val) is str:
            call(nvim, "nvim_set_option_value('%s', '%s', {'win': %d})" % (opt, val, winid))
        elif type(val) is bool:
            if val:
                bool_val = 'v:true'
            else:
                bool_val = 'v:false'
            call(nvim, "nvim_set_option_value('%s', %s, {'win': %d})" % (opt, bool_val, winid))

## if val is a str: no, pass in as 'no', add a quote to it
## if val is a number, pass in as a str
def setbuflocal(nvim, bufnr: int, opt: str, val = None):
    if val is not None:
        if type(val) is int:
            call(nvim, "nvim_set_option_value('%s', %d, {'buf': %d})" % (opt, val, bufnr))
        elif type(val) is str:
            call(nvim, "nvim_set_option_value('%s', '%s', {'buf': %d})" % (opt, val, bufnr))
        elif type(val) is bool:
            if val:
                bool_val = 'v:true'
            else:
                bool_val = 'v:false'
            call(nvim, "nvim_set_option_value('%s', %s, {'buf': %d})" % (opt, bool_val, bufnr))

def appendbufline(nvim, bufnr: int, msg: str):
    call(nvim, "appendbufline(%d, '$', '%s'" % (bufnr, msg))
