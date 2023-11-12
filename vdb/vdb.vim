let g:configs = {}

function s:init_configs() abort
    if !has_key(g:configs, 'dbg')
        let g:configs.dbg = lldb#DBG#init()
    endif
endfunction

let s:DbgCommander = {}
function s:DbgCommander.init() abort
    let self.execute = 0
    let self.interrupt = 0
    return self
endfunction

function g:SetCommander(commander) abort
    let s:DbgCommander = a:commander
endfunction

let s:VDBWin = {}
function s:VDBWin.init() abort
    let self.a = 1
    return self
endfunction

function s:VDBWin.create_win() abort
    
endfunction

function s:VDBWin.show() abort
    
endfunction

function s:VDBWin.hide() abort
    
endfunction

function s:VDBWin.create_buf() abort
    
endfunction

let s:VDBEventHandler = {}
function s:VDBEventHandler.init() abort
    let self.vdb_win = s:VDBWin
endfunction

function s:VDBEventHandler.handle_attached() abort
    
endfunction

let s:VDB = {}
function s:VDB.init(dbg) abort
    let self.dbg_ = dbg
    let self.dbg_.handler = s:VDBEventHandler
    let s:VDBWin = s:VDBWin.init()
    return self
endfunction

function s:VDB.start() abort
    let res = self.dbg_.start()
    if res |return| endif
    let res = s:VDBWin.create_win()
    if res |return| endif
endfunction

function s:VDB.stop() abort
    
endfunction

function s:VDB.execute(cmd) abort
    call self.dbg_.execute(a:cmd)
endfunction

function g:VDBStart() abort
    call s:init_configs()
    let s:VDB = s:VDB.init(g:configs.dbg)
endfunction

function g:VDBStop() abort
    call s:VDB.stop()
endfunction

function g:VDBInterrupt() abort
    
endfunction

function g:VDBExecute(cmd) abort
    call s:VDB.execute(a:cmd)
endfunction