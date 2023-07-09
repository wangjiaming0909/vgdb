let s:Parser = {}

let g:GDB_STATE_UNKNOWN = 0
let g:GDB_STATE_STARTED = 1
let g:GDB_STATE_EXITED = 2

let s:RESULT_REC_TYPE = 0
let s:STREAM_REC_TYPE = 1
let s:ASYNC_REC_TYPE = 2
let s:OTHER_REC_TYPE = 3

let s:ParseRes = {}
let s:Parser.state = g:GDB_STATE_UNKNOWN

function s:ParseRes.Init() abort
  " like {cmd1: key_values1, cmd2: key_values2, ...}
  " key_values like: [{'':'', '':''}, {}]
  " normaly, key_values arr only have 1 ele
  let self.result_recs = {}
  let self.stream_recs = {}
  let self.async_recs = {}
  " like [some output, some output]
  let self.other_recs = []
  return self
endfunction

function! gdbmi#gdbmi_parser#Init() abort
  let s:Parser.gdb_prompt = ''
  let s:Parser.parse_res = s:ParseRes.Init()
  let s:Parser.parse_tmp_recs = []
  return s:Parser
endfunction

function! s:finish_init() abort
  let s:Parser.gdb_prompt = s:Parser.parse_res.other_recs[0]
  let s:Parser.state = g:GDB_STATE_STARTED
endfunction

" parse res will be stored at s:Parser.parse_res
" return 0 if parse finished, 1 if not finished
function! gdbmi#gdbmi_parser#Parse(cmd_res) abort
  if len(a:cmd_res) == 0
    return 0
  endif
  let cmd_recs = a:cmd_res
  if s:Parser.state == g:GDB_STATE_STARTED
    if a:cmd_res[-1] != g:vgdb_prompt && a:cmd_res[-1] != ''
      let s:Parser.parse_tmp_recs = a:cmd_res
      return 1
    else
      if len(s:Parser.parse_tmp_recs) != 0
        let last_rec = s:Parser.parse_tmp_recs[-1]
        let last_rec = last_rec . a:cmd_res[0]
        let s:Parser.parse_tmp_recs[-1] = last_rec
        let cmd_recs = a:cmd_res[1:]
        let cmd_recs = s:Parser.parse_tmp_recs + cmd_recs
        let s:Parser.parse_tmp_recs = []
      endif
    endif
  endif
  call s:Parser.parse_res.Init()
  for msg in cmd_recs
    if msg == ''
      continue
    endif
    let msg = substitute(msg, '\\t', ' ', 'g')
    let msg = trim(msg, "\\n")
    "call Echomsg_if_debug('parse rec ' . msg)
    let fir = strpart(msg, 0, 1)
    if fir == '^'
      call s:parse_result_recs(msg)
    elseif fir == '~' || fir == '&' || fir == '@'
      call s:parse_stream_recs(msg)
    elseif fir == '*' || fir == '='
      call s:parse_async_recs(msg)
    else
      call s:parse_other_recs(msg)
    endif
  endfor
  return 0
endfunction

function! s:parse_from_py(msg) abort
  py3 from pygdbmi import gdbmiparser
  py3 a = vim.eval('a:msg')
  let res = py3eval('gdbmiparser.parse_response(a)')
  return res
endfunction

function! s:parse_result_recs(msg) abort
  "call g:Echomsg_if_debug('parse result rec: ' . a:msg)
  let res = s:parse_from_py(a:msg)
  let cmd_res = res['message']
  let key_values = res['payload']
  if key_values is v:null | let key_values = {} | endif
  "let cmd_res = s:parse_cmd(a:msg)
  "let key_values = s:parse_key_values(cmd_res[1])
  if has_key(s:Parser.parse_res.result_recs, cmd_res)
    call add(s:Parser.parse_res.result_recs[cmd_res], key_values)
  else
    let s:Parser.parse_res.result_recs[cmd_res] = [key_values]
  endif
endfunction

function! s:parse_stream_recs(msg) abort
  "call g:Echomsg_if_debug('parse stream rec: ' . a:msg)
  let cmd_res = s:parse_cmd(a:msg)
  let cmd_res = [a:msg[0], a:msg[2:-2]]
  let key_values = {'value': a:msg[2:-2]}

  if has_key(s:Parser.parse_res.stream_recs, cmd_res[0])
    call add(s:Parser.parse_res.stream_recs[cmd_res[0]], key_values)
  else
    let s:Parser.parse_res.stream_recs[cmd_res[0]] = [key_values]
  endif
endfunction

function! s:parse_async_recs(msg) abort
  "call g:Echomsg_if_debug('parse async rec: ' . a:msg)
  "let cmd_res = s:parse_cmd(a:msg)
  "let key_values = s:parse_key_values(cmd_res[1])

  let res = s:parse_from_py(a:msg)
  let cmd_res = res['message']
  let key_values = res['payload']
  if key_values is v:null | let key_values = {} | endif

  if has_key(s:Parser.parse_res.async_recs, cmd_res)
    call add(s:Parser.parse_res.async_recs[cmd_res], key_values)
  else
    let s:Parser.parse_res.async_recs[cmd_res] = [key_values]
  endif
endfunction

function! s:parse_other_recs(msg) abort
  "call g:Echomsg_if_debug('parse other rec: ' . a:msg)
  call add(s:Parser.parse_res.other_recs, a:msg)
  if s:Parser.state == g:GDB_STATE_UNKNOWN
    call s:finish_init()
  endif
endfunction

"msg is like: ^done,completion="se",matches=["search","section","select-frame","set"],max_completions_reached="0"
"this func will parse ^done
"and return cmd and the remains, here will return: [cmd, ',completion=.....']
function! s:parse_cmd(msg) abort
  "done,completion="se",matches=["search","section","select-frame","set"],max_completions_reached="0"
  let tmp_msg = strpart(a:msg, 1)
  "if only ^done then stridx will return -1, which strpart will return all tmp_msg
  let cmd = tmp_msg[0:stridx(tmp_msg, ',')]
  if stridx(tmp_msg, ',') != -1
    let cmd = cmd[0:-2]
  endif
  "completion="se",matches=["search","section","select-frame","set"],max_completions_reached="0"
  "or empty
  let tmp_msg = tmp_msg[strlen(cmd):-1]
  " remove the last ','
  if stridx(tmp_msg, ',') != -1
    let tmp_msg = tmp_msg[1:]
  endif
  return [cmd, tmp_msg]
endfunction

function! s:parse_key_values(msg) abort
  let key_values = a:msg
  let res = {}
  while key_values != ''
    let equal_sign_idx = stridx(key_values, "=")
    let key = strpart(key_values, 0, equal_sign_idx)
    let char_after_equal = key_values[equal_sign_idx + 1]
    if char_after_equal == '"'
      "echomsg 'value to parse: ' . key_values
      "   some text value
      "   se",matches=...
      let value = key_values[equal_sign_idx + 2:]
      " empty value
      let right_quote_idx = stridx(value, '"')
      if right_quote_idx == 0
        let value = '' "empty value
      else
        while value[right_quote_idx-1] == '\'
          let right_quote_idx = stridx(value, '"', right_quote_idx+1)
        endwhile
        let value = value[:right_quote_idx - 1]
        let value = substitute(value, '\\"', '"', 'g')
      endif
      let res[key] = value
      let key_values = key_values[1 + 2 + strlen(key) + strlen(value):]
      if key_values != ''
        let key_values = key_values[1:]
      endif
    elseif char_after_equal == '['
      call Echomsg_if_debug('arr to parse: ' . key_values)
      " empty arr
      if key_values[equal_sign_idx + 2] == ']'
        let res[key] = []
        let key_values = key_values[equal_sign_idx + 4:]
        continue
      endif

      "    arr value
      "    search","section",....],....
      let arr_str = key_values[equal_sign_idx + 3:]
      let arr = []
      while arr_str != ''
        " the ele is a map
        if key_values[equal_sign_idx + 2] == '{'
          let right_brace_idx = stridx(key_values, '}')
          let map_res = s:parse_key_values(key_values[equal_sign_idx + 3:right_brace_idx - 1])
          call add(arr, map_res)
          let arr_str = key_values[right_brace_idx + 1:]
          let arr_str = arr_str[1:]
          if arr_str[0] == ','
          elseif arr_str[0] == ']'
            break
          endif
          continue
        endif
        " the ele is a value
        let ele = strpart(arr_str, 0, stridx(arr_str, '"'))
        call add(arr, ele)
        "     ,"secion",...],...
        "or   ],...
        let arr_str = arr_str[stridx(arr_str, '"') + 1:]
        " skip the '],' if any
        if arr_str != '' && arr_str[0] == ']'
          let arr_str = arr_str[1:]
          break
        endif
        " skip the ',"' if any
        if arr_str != '' && arr_str[0] == ','
          let arr_str = arr_str[2:]
        endif
      endwhile
      " skip ]
      "     ,...
      "or   empty
      let key_values = arr_str
      if key_values != ''
        "skip ,
        let key_values = key_values[1:]
      endif
      let res[key] = arr
    elseif char_after_equal == '{'
      let right_brace_idx = stridx(key_values, '}')
      let map_str = key_values[equal_sign_idx + 2:right_brace_idx]
      let map_res = s:parse_key_values(map_str)
      let res[key] = map_res
      let key_values = key_values[right_brace_idx+2:]
    else
      echomsg 'some new kind of value found: ' . a:msg
      let key_values = ''
    endif
  endwhile
  return res
endfunction


function Test() abort
  let parser = gdbmi#gdbmi_parser#Init()

  "let parser = gdbmi#gdbmi_parser#Init(
  "      \['=thread-group-added,id="i1"',
  "      \'=cmd-param-changed,param="history filename",value="/root/.gdb_history"',
  "      \'(gdb) '])
  "if s:Parser.state != g:GDB_STATE_STARTED
  "  echomsg 'failed when check state after inited'
  "endif

  echomsg 'testing parse_cmd'
  let cmd_res = s:parse_cmd('^done')
  if cmd_res[0] != "done" || cmd_res[1] != ''
    echomsg 'parse cmd failed for "^done"'
    echomsg cmd_res
  endif

  let cmd_res = s:parse_cmd('^done,completion="se"')
  if cmd_res[0] != 'done' || cmd_res[1] != 'completion="se"'
    echomsg 'parse cmd failed for ^done,completion="se"'
    echomsg cmd_res
  endif
  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'completion') || key_value_res['completion'] != 'se'
    echomsg 'parse cmd failed for ' . '^done,completion="se"'
    echo key_value_res
  endif

  let cmd_res = s:parse_cmd('^running,thread-id="1"')
  if cmd_res[0] != 'running' || cmd_res[1] != 'thread-id="1"'
    echomsg 'parse cmd failed for ' . '^running,thread-id="1"'
    echomsg cmd_res
  endif
  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'thread-id')
        \|| key_value_res['thread-id'] != "1"
    echomsg 'parse cmd failed for ' . '^running,thread-id="1"'
    echo key_value_res
  endif

  let msg = '^done,completion="se",matches=["search","section","select-frame","set"],max_completions_reached="0"'
  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'done'
        \|| cmd_res[1] != 'completion="se",matches=["search","section","select-frame","set"],max_completions_reached="0"'
    echomsg 'parse cmd failed for ' . msg
    echomsg cmd_res
  endif
  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'completion')
        \|| !has_key(key_value_res, 'matches')
        \|| !has_key(key_value_res, 'max_completions_reached')
        \|| key_value_res['completion'] != 'se'
        \|| key_value_res['max_completions_reached'] != '0'
        \|| key_value_res['matches'] != ['search', 'section', 'select-frame', 'set']
    echomsg 'parse key value failed for ' . msg
    echomsg key_value_res
  endif
  
  let msg = '*stopped,reason="breakpoint-hit",disp="keep",bkptno="1",frame={addr="0x00005555555551ee",func="main",args=[],file="./1.cc",fullname="/tmp/1.cc",line="15",arch="i386:x86-64"},thread-id="1",stopped-threads="all",core="6"'
  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'stopped'
        \|| cmd_res[1] != 'reason="breakpoint-hit",disp="keep",bkptno="1",frame={addr="0x00005555555551ee",func="main",args=[],file="./1.cc",fullname="/tmp/1.cc",line="15",arch="i386:x86-64"},thread-id="1",stopped-threads="all",core="6"'
    echomsg 'parse cmd failed for ' . msg
    echomsg cmd_res
  endif
  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'reason')
        \|| key_value_res['reason'] != 'breakpoint-hit'
        \|| !has_key(key_value_res, 'disp')
        \|| key_value_res['disp'] != 'keep'
        \|| !has_key(key_value_res, 'bkptno')
        \|| key_value_res['bkptno'] != '1'
        \|| !has_key(key_value_res, 'thread-id')
    echomsg 'parse key value failed for ' . msg . ' cmd_res: ' . string(key_value_res)
  endif
  echomsg string(key_value_res)

  let msg = '^error,msg="No symbol table is loaded.  Use the \"file\" command."'
  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'error'
        \|| cmd_res[1] != 'msg="No symbol table is loaded.  Use the \"file\" command."'
    echomsg 'parse cmd failed for: ' . msg
    echomsg cmd_res
  endif

  let msg = '^done,completion="",matches=["!","+","-","<",">"]'
  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'done'
        \|| cmd_res[1] != 'completion="",matches=["!","+","-","<",">"]'
  endif
  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'completion')
        \|| !has_key(key_value_res, 'matches')
        \|| key_value_res['completion'] != ''
    echomsg 'parse key value failed for ' . msg
    echomsg key_value_res
  endif

  let msg = '=library-loaded,id="/lib/x86_64-linux-gnu/libm.so.6",target-name="/lib/x86_64-linux-gnu/libm.so.6",host-name="/lib/x86_64-linux-gnu/libm.so.6",symbols-loaded="0",thread-group="i1",ranges=[{from="0x00007ffff7ad1200",to="0x00007ffff7b6ac98"}]'
  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'library-loaded'
        \|| cmd_res[1] != 'id="/lib/x86_64-linux-gnu/libm.so.6",target-name="/lib/x86_64-linux-gnu/libm.so.6",host-name="/lib/x86_64-linux-gnu/libm.so.6",symbols-loaded="0",thread-group="i1",ranges=[{from="0x00007ffff7ad1200",to="0x00007ffff7b6ac98"}]'
    echomsg 'parse cmd failed for: ' . msg
    echomsg cmd_res
  endif

  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'id')
        \|| !has_key(key_value_res, 'target-name')
        \|| !has_key(key_value_res, 'host-name')
        \|| !has_key(key_value_res, 'symbols-loaded')
        \|| !has_key(key_value_res, 'ranges')
    echomsg 'parse key value failed for: ' . msg
    echomsg key_value_res
  endif

  let msg = '*stopped,reason="signal-received",signal-name="SIGINT",signal-meaning="Interrupt",frame={addr="0x00007ffff7cca14a",func="__GI___clock_nanosleep",args=[{name="clock_id",value="0"},{name="clock_id@entry",value="0"},{name="flags",value="0"},{name="flags@entry",value="0"},{name="req",value="<optimized out>"},{name="rem",value="<optimized out>"}],file="../sysdeps/unix/sysv/linux/clock_nanosleep.c",fullname="./time/../sysdeps/unix/sysv/linux/clock_nanosleep.c",line="79",arch="i386:x86-64"},thread-id="1",stopped-threads="all",core="14"'

  let cmd_res = s:parse_cmd(msg)
  if cmd_res[0] != 'stopped'
    echomsg 'parse cmd failed for: ' . msg
    echomsg cmd_res
  endif

  let key_value_res = s:parse_key_values(cmd_res[1])
  if !has_key(key_value_res, 'reason')
        \|| !has_key(key_value_res, 'frame')
        \|| !has_key(key_value_res, 'thread-id')
    echomsg 'parse key value failed for: ' . msg
    echomsg key_value_res
  endif

endfunction

function A() abort
  py3 from pygdbmi import gdbmiparser
  py3 a = '*stopped,reason="signal-received",signal-name="SIGINT",signal-meaning="Interrupt",frame={addr="0x00007ffff7cca14a",func="__GI___clock_nanosleep",args=[{name="clock_id",value="0"},{name="clock_id@entry",value="0"},{name="flags",value="0"},{name="flags@entry",value="0"},{name="req",value="<optimized out>"},{name="rem",value="<optimized out>"}],file="../sysdeps/unix/sysv/linux/clock_nanosleep.c",fullname="./time/../sysdeps/unix/sysv/linux/clock_nanosleep.c",line="79",arch="i386:x86-64"},thread-id="1",stopped-threads="all",core="14"'
  echo py3eval('gdbmiparser.parse_response(a)')
  "{'token': v:null, 'message': 'stopped', 'type': 'notify',
  "  'payload': {
  "    'reason': 'signal-received', 'thread-id': '1',
  "    'stopped-threads': 'all', 'signal-name': 'SIGINT',
  "    'core': '14', 'signal-meaning': 'Interrupt',
  "    'frame': {
  "      'file': '../sysdeps/unix/sysv/linux/clock_nanosleep.c',
  "      'line': '79', 'func': '__GI___clock_nanosleep',
  "      'args': [
  "        {'name': 'clock_id', 'value': '0'},
  "        {'name': 'clock_id@entry', 'value': '0'},
  "        {'name': 'flags', 'value': '0'},
  "        {'name': 'flags@entry', 'value': '0'},
  "        {'name': 'req', 'value': '<optimized out>'},
  "        {'name': 'rem', 'value': '<optimized out>'}
  "      ],
  "      'arch': 'i386:x86-64', 'addr': '0x00007ffff7cca14a',
  "      'fullname': './time/../sysdeps/unix/sysv/linux/clock_nanosleep.c'
  "    }
  "  }
  "}
endfunction
