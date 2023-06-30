let s:gdb_win_id = -1
let s:gdb_win_buf = -1
let g:vgdb_prompt = ''
let g:gdb_win_width = 40
let s:gdb_console_file = '/tmp/gdb_console'
let g:gdb_mi_output = ''
let s:gdb_job = -1
let g:gdb_bin = 'gdb'
let g:debug = 0
let s:gdb_buf_nr = -1

function! g:Echomsg_if_debug(str) abort
  if g:debug == 1
    echomsg a:str
  endif
endfunction

function GDBWin_Create() abort
  if s:gdb_buf_nr == -1
    silent! execute '!echo "--------Welcome TO VGDB--------" > ' . s:gdb_console_file
  endif
  silent! execute 'vertical topleft ' . g:gdb_win_width . ' split ' . s:gdb_console_file
  let s:gdb_win_id = win_getid()
  call Echomsg_if_debug('create gdb win win id: ' . s:gdb_win_id)
  call s:ensure_buf_loaded(s:gdb_win_id)
  let s:gdb_buf_nr = bufnr()
  call s:init_gdb_win()
  call cursor('$', 999)
endfunction

function s:setup_prompt() abort
  call appendbufline(s:gdb_buf_nr, "$", g:vgdb_prompt)
  call cursor('$', 999)
endfunction

function s:go_to_original_win_and_key_and_comeback(key) abort
  if s:original_win_id != 0
    call win_gotoid(s:original_win_id)
    normal! zz
    call win_gotoid(s:gdb_win_id)
  endif
endfunction

" we assume we have moved to gdbwin
function s:init_gdb_win() abort
  setl noequalalways
  setl signcolumn=no
  setl nonu
  setl bh=hide
  "setl noswapfile
  setl buftype=prompt
  call prompt_setprompt(bufnr(''), '')
  setl completeopt=menu,longest,preview
  "autocmd CursorMovedI 
  setl lcs=tab:**
  "setl autowriteall
  setl cursorline
  "setl nobuflisted
  setl completefunc=GDBWin_Complete
  "set scrolloff=10
  setl statusline=%<%F[%1*%M%*%n%R%H]
  "setl completeopt=preview
  "
  nnoremap <buffer><expr>i <SID>gdb_win_modifiable() ? "i" : "GA"
  nnoremap <buffer><expr>a <SID>gdb_win_modifiable(-1) ? "a" : "GA"
  nnoremap <buffer><expr>o <SID>gdb_win_modifiable() ? "GA" : "GA"
  " 03wi only working for gdb prompt as '(gdb) '
  nnoremap <buffer><expr>I <SID>gdb_win_modifiable() ? "03wi" : "GA"
  nnoremap <buffer><expr>A <SID>gdb_win_modifiable() ? "A" : "GA"
  nnoremap <buffer><expr>O <SID>gdb_win_modifiable() ? "GA" : "GA"
  nnoremap <buffer><expr> 0 <SID>gdb_win_buf_in_last_line() ? "03w" : "0"
  nmap <buffer><expr> 8 <sid>gdb_win_buf_in_last_line() ? "\<UP>0la (*<ESC>A)<cr><ESC>" : "8"

  inoremap <expr> <buffer> <BS> <SID>gdb_win_modifiable(1) ? "\<BS>" : ""
  nnoremap <expr> <buffer> x <SID>gdb_win_modifiable() ? "x" : ""
  nnoremap <expr> <buffer> d <SID>gdb_win_modifiable() ? "d" : ""
  nnoremap <expr> <buffer> dd <SID>gdb_win_modifiable() ? "ddo".g:vgdb_prompt :
        \ <SID>gdb_win_buf_in_last_line() ? "A" : ""
  "nnoremap <expr> <buffer> c <SID>gdb_win_modifiable() ? "c" : ""
  nnoremap c :silent! call <SID>GDBMI_Execute('c', 1)<cr>
  nnoremap <expr> <buffer> s <SID>gdb_win_modifiable() ? "s" : ""
  nnoremap <expr> <buffer> cc <SID>gdb_win_modifiable() ? "cc". g:vgdb_prompt :
        \ <SID>gdb_win_buf_in_last_line() ? "A" : ""
  nnoremap <expr> <buffer> p "GAp "
  inoremap <buffer> <CR> <ESC>:silent! call VGDB_Execute()<CR>A
  nnoremap <buffer> <CR> :silent! call VGDB_Execute()<CR>

  nnoremap <buffer><expr> u <SID>gdb_win_modifiable() ? "u" : ""

  inoremap <buffer><silent><UP> <ESC>:call GDBWin_History_Up("")<CR>A
  inoremap <buffer><silent><Down> <ESC>:call GDBWin_History_Down("")<CR>A
  nnoremap <buffer><silent><UP> <ESC>:call GDBWin_History_Up("")<CR>
  nnoremap <buffer><silent><Down> <ESC>:call GDBWin_History_Down("")<CR>
  "nnoremap <buffer><silent> j :call <SID>go_to_original_win_and_key('j')<CR>
  "nnoremap <buffer><silent> k :call <SID>go_to_original_win_and_key('k')<CR>
  "nnoremap <buffer><silent> h :call <SID>go_to_original_win_and_key('h')<CR>
  "nnoremap <buffer><silent> l :call <SID>go_to_original_win_and_key('l')<CR>
  nnoremap <buffer><silent> zz zz:call <SID>go_to_original_win_and_key_and_comeback('zz')<CR>
  inoremap <buffer><silent><c-j> <ESC>:call GDBWin_History_Down("")<CR>A
  nnoremap <buffer><silent><c-j> :call GDBWin_History_Down("")<CR>
  inoremap <buffer><silent><c-k> <ESC>:call GDBWin_History_Up("")<CR>A
  nnoremap <buffer><silent><c-k> :call GDBWin_History_Up("")<CR>
  inoremap <expr> <buffer> <silent> <TAB> pumvisible() ? "\<C-n>" : "\<C-x><C-u>"
  "inoremap <expr> <buffer> <silent> <S-TAB> "\<C-p>"
  inoremap <buffer> <silent> <c-c> <ESC>:call VGDB_Interrupt()<cr>A
  nnoremap <buffer> <silent> <c-c> :call VGDB_Interrupt()<cr>

  hi DbgBreakPoint    guibg=darkblue  ctermfg=none term=reverse ctermbg=3
  hi DbgDisabledBreak guibg=lightblue guifg=none ctermfg=none ctermbg=202
  hi DbgPC            guibg=Orange    guifg=none gui=bold ctermbg=17 ctermfg=none
  sign define DebugBP  numhl=DbgBreakPoint  text=B>
  sign define DebugDBP numhl=DbgDisabledBreak linehl=DbgDisabledBreak text=b> texthl=DbgDisabledBreak
  sign define DebugPC  linehl=DbgPC            text=>> texthl=DbgPC
endfunction

function! s:gdb_win_buf_in_last_line() abort
  if getpos('.')[1] == line('$')
    return 1
  endif
  return 0
endfunction

function! s:go_to_gdb_win() abort
  if bufwinnr(s:gdb_buf_nr) == -1
    call GDBWin_Show()
  endif
  call win_gotoid(s:gdb_win_id)
endfunction

function! s:gdb_win_key(key) abort
  call s:go_to_gdb_win()
  call cursor('$', 999)
  call feedkeys('A'. a:key .' ')
endfunction

" this function do not assume cursor is in s:gdb_win_id
function! s:gdb_win_append(str) abort
  if a:str == '' | return | endif
  if a:str != ''
    call appendbufline(s:gdb_buf_nr, '$', a:str)
  endif
  call win_execute(s:gdb_win_id, "call cursor('$', 999)")
endfunction

function! s:gdb_win_set_cur_line(str) abort
  if line('.') != line('$') || col('.') != col('$')
    call cursor('$', 999)
  endif
  call setline('.', g:vgdb_prompt . a:str)
  call cursor('$', 999)
endfunction

function! s:gdb_win_modifiable(extra_col = 0) abort
  "[bufnum, lnum, col, off]
  let pos = getpos('.')
  if pos[1] != line('$')
    return 0
  endif
  if strpart(getline('.'), 0, len(g:vgdb_prompt)) == g:vgdb_prompt
    if pos[2] <= len(g:vgdb_prompt) + a:extra_col
      return 0
    endif
  endif
  return 1
endfunction

function! s:gdb_win_load_buf(fullname, line) abort
  let fullname = a:fullname
  let line = a:line
  if filereadable(fullname)
    let bufnr = s:ensure_buf_loaded(fullname)
    " if we are not in gdb win
    if bufwinid(s:gdb_buf_nr) != win_getid()
      exec 'buffer ' . fullname
      call cursor(line, 1)
    else
      "if we are in gdb win
      "if the original win has been closed
      if win_id2win(s:original_win_id) == 0
        let width = &columns - g:gdb_win_width
        silent execute 'vertical botright ' . width .  ' split ' . fullname
        call s:ensure_buf_loaded(fullname)
        call cursor(line, 1)
        let s:original_win_id = win_getid()
      else
        "the original window not closed
        let a_win_id = win_getid()
        call win_gotoid(s:original_win_id)
        exec 'buffer ' . bufnr
        call cursor(line, 1)
        call win_gotoid(a_win_id)
      endif
    endif
    return 1
  endif
  return 0
endfunction

function! s:place_pc_sign(name, fullname, line) abort
  if s:pc_sign_id != -1 | call sign_unplace('', {'id': s:pc_sign_id}) | endif
  let s:pc_sign_id = sign_place(0, "", a:name, a:fullname, {'lnum': a:line, 'priority': 100})
endfunction

function! s:unplace_pc_sign() abort
  if s:pc_sign_id != -1 | call sign_unplace('', {'id': s:pc_sign_id}) | endif
  let s:pc_sign_id = -1
endfunction

function s:ensure_buf_loaded(filename) abort
  if !bufexists(a:filename)
    let bufnr = bufadd(a:filename)
    call bufload(bufnr)
  endif
  return bufnr(a:filename)
endfunction

function! GDBWin_Show() abort
  if s:gdb_buf_nr == -1 || bufwinnr(s:gdb_buf_nr) == -1
    call GDBWin_Create()
    call s:restore_original_maps()
  else
    if bufwinnr(s:gdb_buf_nr) == -1
      silent! execute 'vertical topleft ' . g:gdb_win_width . ' split' . s:gdb_console_file
      let s:gdb_win_id = win_getid()
      call Echomsg_if_debug('recreate gdb win')
    else
      call GDBWin_Hide()
    endif
  endif
endfunction

function! s:unmap_original_maps() abort
  for key in keys(s:original_win_unmap)
    execute s:original_win_unmap[key]
  endfor
endfunction

function! s:restore_original_maps() abort
  for key in keys(s:original_win_map)
    execute s:original_win_map[key]
  endfor
endfunction

" we are in gdb win now
function! s:record_gdb_win_width() abort
  let w = winwidth(0)
  let g:gdb_win_width = w
endfunction

function! GDBWin_Hide() abort
  if bufwinnr(s:gdb_buf_nr) == -1
    return
  endif
  call s:go_to_gdb_win()
  call s:record_gdb_win_width()
  hide
  call s:unmap_original_maps()
  let s:gdb_win_id = -1
endfunction

function! GDBWin_History_Up(key) abort
  let cmd = s:GDBMI.gdb_his.Up()
  call s:gdb_win_set_cur_line(cmd)
endfunction

function! GDBWin_History_Down(key) abort
  let cmd = s:GDBMI.gdb_his.Down()
  call s:gdb_win_set_cur_line(cmd)
endfunction

function! GDBWin_Complete(findstart, base)
  if a:findstart
    let line = getline('$')
    let cmd = strpart(line, len(g:vgdb_prompt))
    let s:complete_cmd = cmd

    "return len(g:vgdb_prompt)
    let line = getline('.')
    let start = col('.') - 1
    while start > 0 && line[start - 1] =~ '\S' && line[start-1] != '*' "fixed *pointer
      let start -= 1
    endwhile
    let s:complete_cmd = line[len(g:vgdb_prompt):col('.')-2]
    let s:start = start
    return start
  endif
  let res = s:GDBMI.Complete(s:complete_cmd)
  call Echomsg_if_debug('complete res ' . string(res) . ' start: ' . s:start)
  let new_res = []
  for cmd in res
    call add(new_res, strpart(cmd, s:start-len(g:vgdb_prompt)))
  endfor
  call Echomsg_if_debug('new complete res ' . string(new_res))
  return new_res
endfunction

let s:GDBCmdHistory = {}
let s:GDBCmdCompleter = {}

function s:GDBCmdHistory.Init() abort
  let self.hises = []
  let self.MAX_HIS_NUM = 64
  let self.cur_his_idx = -1
  return self
endfunction

function s:GDBCmdHistory.Add(cmd) abort
  if len(self.hises) == self.MAX_HIS_NUM
    let self.hises = s:GDBCmdHistory.hises[:-1]
  endif
  if len(self.hises) > 0 && self.hises[0] == a:cmd | return | endif
  call insert(self.hises, a:cmd)
endfunction

function s:GDBCmdHistory.Up() abort
  if self.cur_his_idx == -1
    let self.original_cmd = strpart(getline('$'), len(g:vgdb_prompt))
  endif
  if len(self.hises) == self.cur_his_idx + 1
    if len(self.hises) > 0 | return self.hises[self.cur_his_idx]
    else | return self.original_cmd
    endif
  else
    let self.cur_his_idx += 1
    return self.hises[self.cur_his_idx]
  endif
endfunction

function s:GDBCmdHistory.Down() abort
  if self.cur_his_idx == -1
    let self.original_cmd = strpart(getline('$'), len(g:vgdb_prompt))
    return self.original_cmd
  endif
  if self.cur_his_idx == 0 | let self.cur_his_idx -= 1 | return self.original_cmd
  else
    let self.cur_his_idx -= 1 | return self.hises[self.cur_his_idx]
  endif
endfunction

function s:GDBCmdHistory.Reset() abort
  let self.cur_his_idx = -1
endfunction

function s:GDBCmdCompleter.Init(gdbmi_ins) abort
  let self.gdbmi_ins = a:gdbmi_ins
  let self.completes = []
  let self.complete_completed = 0
  return self
endfunction

function s:GDBCmdCompleter.Complete(prefix) abort
  let self.completes = []
  let cmd = '-complete "' . a:prefix . '"'
  let self.complete_completed = 0
  call self.gdbmi_ins.Execute(cmd)
  let times = 0
  while !self.complete_completed
    if times >= 1000 | break | endif
    sleep 5m
    let times += 1
  endwhile
  return self.completes
endfunction

let s:GDBMIParser = {}

let s:GDBMI_STATE_UNKNOWN = 0
let s:GDBMI_STATE_STARTED = 1
let s:GDBMI_STATE_EXITED = 2

let s:PROGRAM_STATE_STOPPED = 0
let s:PROGRAM_STATE_BK_HIT = 1
let s:PROGRAM_STATE_RUNNING = 2

let s:GDBMI = {}

function s:GDBMI.Init() abort
  let self.gdb_cmd = [g:gdb_bin, '-q', '--nw', '--interpreter=mi3']
  let self.job_id = -1
  let self.stdout_cb = function(s:GDBMI.on_stdout, s:GDBMI)
  let self.stderr_cb = function(s:GDBMI.on_stderr, s:GDBMI)
  let self.exit_cb = function(s:GDBMI.on_exit_cb, s:GDBMI)
  let self.program_state = s:PROGRAM_STATE_STOPPED
  let self.gdb_state = s:GDBMI_STATE_UNKNOWN
  let self.gdb_his = s:GDBCmdHistory.Init()
  let self.gdbmi_parser = gdbmi#gdbmi_parser#Init()
  let self.gdbmi_completer = s:GDBCmdCompleter.Init(self)
  let self.breakpoints = {}
  let self.in_complete_mode = 0
  let self.gdb_mi_output = ''
  let self.gdb_cmd_opt = {
        \'on_stdout': self.stdout_cb,
        \'on_stderr': self.stderr_cb,
        \'on_exit': self.exit_cb
        \}
  return self
endfunction

function s:GDBMI.on_stdout(id, data, event) abort
  "call g:Echomsg_if_debug('on stdout ' . a:id . ' ' . a:event)
  for msg in a:data | call g:Echomsg_if_debug('on stdout: ' . msg) | endfor

  if gdbmi#gdbmi_parser#Parse(a:data) != 0 | return | endif
  if len(g:vgdb_prompt) == 0 | let g:vgdb_prompt = self.gdbmi_parser.gdb_prompt | endif
  call Echomsg_if_debug('parse res: ' . string(self.gdbmi_parser.parse_res))
  call self.handle_parse_res(self.gdbmi_parser.parse_res)
endfunction

function s:GDBMI.on_stderr(id, data, event) abort
  call g:Echomsg_if_debug('on stderr ' . a:id . ' ' . a:event)
  for msg in a:data | call self.output_to_win(msg) | endfor
  "for msg in a:data
    "echomsg 'on stderr: ' . msg
  "endfor
  "call s:GDBMIParser.start_parse(a:data)
endfunction

function s:GDBMI.on_exit_cb(id, data, event) abort
  call self.output_to_win(a:data)
  call self.Exit()
  "echomsg 'on exit ' . a:id . ' ' . a:event
  "call s:GDBMIParser.start_parse(a:data)
endfunction

function s:GDBMI.Exit() abort
  call self.remove_all_bk()
  call s:unplace_pc_sign()
  if bufwinnr(s:gdb_buf_nr) != 0
    let win_id = bufwinid(s:gdb_buf_nr)
    call win_gotoid(win_id)
    execute 'bdelete!'
  else
    execute 'bdelete! ' . bufname(s:gdb_buf_nr)
  endif
  let s:gdbmi_started = 0
  let s:original_win_id = 0
  let s:gdb_win_id = -1
  let s:gdb_buf_nr = -1
endfunction

let s:pc_sign_id = -1
function s:GDBMI.handle_frame_rec(frame) abort
  let frame = a:frame
  if !has_key(frame, 'fullname')
    echomsg 'some frame rec without fullname: ' . string(frame)
    return
  endif
  let fullname = frame['fullname']
  let line = frame['line']
  call Echomsg_if_debug('stopped, fillname is: ' . fullname . ' line: ' . line)
  if s:gdb_win_load_buf(fullname, line)
    call s:place_pc_sign('DebugPC', fullname, line)
  endif
endfunction

" stopped_rec is map, like: {reason="breakpoint-hit",disp="keep",bkptno="1"...}
function s:GDBMI.handle_stopped(stopped_rec) abort
  if has_key(a:stopped_rec, 'reason')
    let reason = a:stopped_rec['reason']
    if reason == 'breakpoint-hit'
          \|| reason == 'end-stepping-range'
          \|| reason == 'signal-received'
          \|| reason =='function-finished'
      let self.program_state = s:PROGRAM_STATE_BK_HIT
      let frame = a:stopped_rec['frame']
      call self.handle_frame_rec(frame)
      return
    endif
  elseif has_key(a:stopped_rec, 'frame')
    let self.program_state = s:PROGRAM_STATE_BK_HIT
    let frame = a:stopped_rec['frame']
    call self.handle_frame_rec(frame)
  endif
endfunction

function s:GDBMI.handle_other_recs(recs) abort
  let recs = a:recs
  if self.in_complete_mode | return | endif
  for rec in recs.other_recs | call self.output_to_win(rec) | endfor
endfunction

function s:GDBMI.handle_completion_rec(completes) abort
  call Echomsg_if_debug("setting completes: " . string(a:completes))
  let self.gdbmi_completer.complete_completed = 1
  let self.gdbmi_completer.completes = a:completes
endfunction

function s:GDBMI.get_bk(bkpt_map) abort
  let bk = {}
  let bk.fullname = a:bkpt_map['fullname']
  let bk.line = a:bkpt_map['line']
  let bk.id = a:bkpt_map['number']
  let bk.enabled = a:bkpt_map['enabled'] == 'y'
  let bk.sign_id = -1
  return bk
endfunction

function s:GDBMI.add_bk(bk) abort
  let self.breakpoints[a:bk.id] = a:bk
  call s:ensure_buf_loaded(a:bk.fullname)
  if a:bk.enabled
    let sign_id = sign_place(0, "", 'DebugBP', a:bk.fullname, {'lnum': a:bk.line})
    let self.breakpoints[a:bk.id].sign_id = sign_id
    call Echomsg_if_debug('place sign id: ' . sign_id . ' for bk: ' . string(a:bk))
  else
    let sign_id = sign_place(0, "", 'DebugDBP', a:bk.fullname, {'lnum': a:bk.line})
    let self.breakpoints[a:bk.id].sign_id = sign_id
  endif
endfunction

function s:GDBMI.has_bk(name, line) abort
  for id in keys(self.breakpoints)
    let bk = self.breakpoints[id]
    if bufnr(bk.fullname) == bufnr(a:name)
          \&& a:line == bk.line
      return id
      break
    endif
  endfor
  return -1
endfunction

function s:GDBMI.remove_all_bk() abort
  for id in keys(self.breakpoints)
    call self.remove_bk(id)
  endfor
endfunction

function s:GDBMI.remove_bk(bk_id) abort
  let bk = self.breakpoints[a:bk_id]
  let msg = 'bk deleted: ' . bk.fullname . ' line: ' . bk.line
  call self.output_to_win(msg)
  call Echomsg_if_debug('unplace sign id: ' . bk.sign_id . ' for bk: ' . string(bk))
  call sign_unplace('', {'id': bk.sign_id})
  call sign_unplace('', {'id': bk.sign_id})
  unlet self.breakpoints[a:bk_id]
endfunction

function s:GDBMI.handle_bk_event(key, value) abort
  if a:key == 'breakpoint-created'
    let bkpt_map = a:value['bkpt']
    if !has_key(bkpt_map, 'fullname')
      return
    endif
    let bk = self.get_bk(bkpt_map)
    call self.add_bk(bk)
  elseif a:key == 'breakpoint-deleted'
    let bk_id = a:value['id']
    call self.remove_bk(bk_id)
  else
  endif
endfunction

" * =
function s:GDBMI.handle_async_recs(recs) abort
  let recs = a:recs
  for async_rec_key in keys(recs.async_recs)
    if async_rec_key == 'running'
      let self.program_state = s:PROGRAM_STATE_RUNNING
      for running_rec in recs.async_recs[async_rec_key]
        "call self.output_to_win(string(running_rec))
      endfor
      call s:unplace_pc_sign()
    elseif async_rec_key == 'stopped'
          \|| async_rec_key == 'thread-selected'
      for stopped_rec in recs.async_recs[async_rec_key]
        call self.handle_stopped(stopped_rec)
      endfor
    elseif async_rec_key == 'library-loaded'
      continue
    elseif async_rec_key == 'breakpoint-created'
          \|| async_rec_key == 'breakpoint-modified'
          \|| async_rec_key == 'breakpoint-deleted'
      let value = recs.async_recs[async_rec_key]
      for bkpt in value
        call self.handle_bk_event(async_rec_key, bkpt)
      endfor
      continue
    elseif async_rec_key == 'thread-group-started'
      continue
    else
      "some other recs
      for other_async_rec in recs.async_recs[async_rec_key]
        call self.output_to_win(async_rec_key . ':' . string(other_async_rec))
      endfor
    endif
  endfor
endfunction

"~"#1  0x000055555555528d in main () at 1.cc:49\n"
function s:GDBMI.handle_frame_async_rec(value) abort
  let val = trim(a:value)
  let last_at_idx = strridx(val, 'at')
  if last_at_idx != 0
    let file_line = val[last_at_idx + 3:]
    let file_line_arr = split(file_line, ':')
    call Echomsg_if_debug('file line arr: ' . file_line_arr[0] . ' file line arr1: ' . file_line_arr[1])
    call s:gdb_win_load_buf(file_line_arr[0], file_line_arr[1])
  endif
endfunction

" ~ & @
function s:GDBMI.handle_stream_recs(recs) abort
  let recs = a:recs
  for stream_rec_key in keys(recs.stream_recs)
    if stream_rec_key == '~'
      for cli_resp in recs.stream_recs[stream_rec_key]
        let val = cli_resp['value']
        if stridx(val, '#') == 0
          call s:GDBMI.handle_frame_async_rec(val)
        endif
        if stridx(val, 'Starting program') == 0 || !empty(matchstr(val, 'process.*killed'))
          call s:unplace_pc_sign()
        endif
        call self.output_to_win(val)
      endfor
    elseif stream_rec_key == '@'
      for target_output in recs.stream_recs[stream_rec_key]
        call self.output_to_win(cli_resp['value'])
      endfor
    elseif stream_rec_key == '&'
      for output in recs.stream_recs[stream_rec_key]
        if has_key(output, 'value') && output['value'] == 'detach'
          call s:unplace_pc_sign()
        endif
      endfor
      " do nothing, eat the output
    else
      "should not be here
      echomsg "some stream recs not handled"
      echomsg recs
    endif
  endfor
endfunction

let s:last_msg = ''
function s:GDBMI.output_to_win(msg) abort
  if a:msg == ''| return | endif
  if s:last_msg == g:vgdb_prompt && g:vgdb_prompt != '' && a:msg == g:vgdb_prompt
    "call Echomsg_if_debug('output msg to win, but filtered: ' . a:msg)
    "return
  endif
  call Echomsg_if_debug('msgs: ' . a:msg . '|' . g:vgdb_prompt . '|' . s:last_msg . '|')
  let s:last_msg = a:msg
  let msg = a:msg
  let msg = substitute(msg, '\\\\', '\\', 'g')
  let msg = substitute(msg, "\\'", "'", 'g')
  let msg = substitute(msg, '\\"', '"', 'g')
  call Echomsg_if_debug('output msg to win: ' . msg)
  call s:gdb_win_append(msg)
  if self.program_state == s:PROGRAM_STATE_RUNNING && a:msg != '' && a:msg != g:vgdb_prompt
    "call s:setup_prompt()
  endif
endfunction

" done_rec is dict, like {'completion': 'se', 'matches': ...}
function s:GDBMI.handle_done_rec(done_rec) abort
  if has_key(a:done_rec, 'matches')
    call self.handle_completion_rec(a:done_rec['matches'])
  endif
endfunction

" ^
function s:GDBMI.handle_res_recs(recs) abort
  let recs = a:recs
  for res_rec_key in keys(recs.result_recs)
    if res_rec_key == 'done'
      for done_rec in recs.result_recs['done']
        call self.handle_done_rec(done_rec)
      endfor
    elseif res_rec_key == 'error'
      let err_res_arr = recs.result_recs['error']
      for err_msg in err_res_arr
        call self.output_to_win(err_msg['msg'])
      endfor
    elseif res_rec_key == 'running'
      let self.program_state = s:PROGRAM_STATE_RUNNING
      " do nothing
    else
      " just output_to_win
        call self.output_to_win(res_rec_key . ': ' . string(recs.result_recs[res_rec_key]))
    endif
  endfor
endfunction

function s:GDBMI.handle_parse_res(recs) abort
  "call g:Echomsg_if_debug(self.gdbmi_parser.parse_res)
  let recs = a:recs
  " check result rec first
  call self.handle_res_recs(recs)
  " then check async rec
  call self.handle_async_recs(recs)
  call self.handle_stream_recs(recs)
  call self.handle_other_recs(recs)
endfunction

function s:GDBMI.Execute(cmd) abort
  call g:Echomsg_if_debug('job_id: '. self.job_id . 'start to execute: ' . a:cmd)
  call jobsend(self.job_id, a:cmd . "\n")
endfunction

function s:GDBMI.Complete(prefix) abort
  let self.in_complete_mode = 1
  return self.gdbmi_completer.Complete(a:prefix)
endfunction

" return job_id if succeed, otherwise -1
function s:GDBMI.Start() abort
  let self.job_id = jobstart(self.gdb_cmd, self.gdb_cmd_opt)
  if self.job_id > 0
    return self.job_id
  endif
  return -1
endfunction

let s:gdbmi_started = 0
function! s:GDBMI_Start() abort
  let s:GDBMI = s:GDBMI.Init()
  call s:GDBMI.Start()
  let s:gdbmi_started = 1
  return s:GDBMI.job_id
endfunction

function! s:GDBMI_Exit() abort
endfunction

function! s:GDBMI_Execute(cmd, ignore_his = 0) abort
  let s:GDBMI.gdb_mi_output = ''
  let s:GDBMI.in_complete_mode = 0
  if !a:ignore_his
    call s:GDBMI.gdb_his.Reset()
    call s:GDBMI.gdb_his.Add(a:cmd)
  endi
  call s:GDBMI.Execute(a:cmd)
endfunction

function! s:GDBMI_Toggle_Break() abort
  " if we are in gdb win, then we go to original_win and set break point
  if s:gdb_buf_nr == bufnr()
    call win_gotoid(s:original_win_id)
  endif
  let b_name = bufname(bufnr())
  let line_n = line(".")
  let cmd = 'b ' . b_name . ':' . line_n
  let bk_id =  s:GDBMI.has_bk(b_name, line_n)
  if bk_id != -1
    call s:GDBMI.Execute('delete breakpoints ' . bk_id)
  else
    call s:GDBMI.Execute(cmd)
  endif
endfunction

" we are in the original win now
function! s:setup_original_win() abort
  nnoremap <F10> :silent! call <SID>GDBMI_Execute('n', 1)<cr>
  nnoremap <F11> :silent! call <SID>GDBMI_Execute('s', 1)<cr>
  nunmap <F9>
  nnoremap <F9> :silent! call <SID>GDBMI_Execute('fin', 1)<cr>
  nnoremap <F8> :silent! call <SID>GDBMI_Execute('f', 1)<cr>
  nnoremap c :silent! call <SID>GDBMI_Execute('c', 1)<cr>
  nnoremap <c-c> :call VGDB_Interrupt()<cr>
  nnoremap p :silent! call <SID>gdb_win_key('p')<cr>

  nnoremap <c-up> :silent! call <SID>GDBMI_Execute('up', 1)<cr>
  nnoremap <c-down> :silent! call <SID>GDBMI_Execute('down', 1)<cr>
  inoremap <c-up> :silent! call <SID>GDBMI_Execute('up', 1)<cr>
  inoremap <c-down> :silent! call <SID>GDBMI_Execute('down', 1)<cr>

  nnoremap <C-B> :silent! call <SID>GDBMI_Toggle_Break()<cr>
  nnoremap L :silent! call <sid>GDBMI_Execute('info locals', 1)<cr>
  nunmap t
  nnoremap t :silent! call <sid>gdb_win_key('t')<cr>

  let s:original_win_unmap = {
        \'p': 'nunmap p',
        \'c': 'nunmap c'
        \}
  let s:original_win_map = {
        \'p': "nnoremap p :silent! call <SID>gdb_win_key('p')<cr>",
        \'c': "nnoremap c :silent! call <SID>GDBMI_Execute('c', 1)<cr>"
        \}
  set mouse=a
  set signcolumn=no
endfunction

let s:original_win_id = 0
function! VGDB_Start() abort
  if s:original_win_id == 0
    let s:original_win_id = win_getid()
    call Echomsg_if_debug('original win id ' . s:original_win_id)
    call s:setup_original_win()
  endif
  if s:gdb_win_id == -1 | call GDBWin_Show() | endif

  if !s:gdbmi_started
    let mi_res = s:GDBMI_Start()
    if mi_res < 0 | throw 'start gdb failed' | endif
  endif
endfunction

function! VGDB_Interrupt() abort
  if s:GDBMI.job_id < 0
        \|| s:GDBMI.program_state == s:PROGRAM_STATE_STOPPED
        \|| s:GDBMI.program_state ==  s:PROGRAM_STATE_BK_HIT
    call s:gdb_win_append('Quit')
    call s:setup_prompt()
    return
  endif
  let pid = jobpid(s:GDBMI.job_id)
  call system('kill -2 ' . pid)
endfunction

let s:last_cmd = ''
function! VGDB_Execute() abort
  let line = getline('.')
  let cmd = strpart(line, len(g:vgdb_prompt))
  if cmd == '' && s:last_cmd == '' | call s:gdb_win_append('') | return
  elseif cmd == '' | let cmd = s:last_cmd | endif
  let s:last_cmd = cmd
  call s:GDBMI_Execute(cmd)
endfunction
