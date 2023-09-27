function! float#Preview(title, txt) abort
  let rows = split(a:txt, "\n")
  let max_len = 0
  for r in rows
    let max_len = max([max_len, len(r)])
  endfor
  let row = len(rows)
  let col = max_len
  let width = col + 10
  let height = row + 4
  let buf_nr = s:create_float_win(a:title, row, col, width, height)
  for r in rows
    if trim(r) == '' | continue | endif
    call appendbufline(buf_nr, '0', trim(r))
  endfor
endfunction

let s:float_buf_nr = -1
let s:win_handle = -1
function! s:create_float_win(title, row, col, width, height) abort
  if s:win_handle != -1 && bufloaded('_float_buffer')
    call nvim_win_close(s:win_handle, 1)
    let s:win_handle = -1
  endif
  let s:float_buf_nr = bufadd('_float_buffer')
  call nvim_buf_set_lines(s:float_buf_nr, 0, -1, 0, [])
  let s:win_handle = nvim_open_win(s:float_buf_nr, 0, {
        \'relative':'cursor',
        \'row':1,
        \'col':1,
        \'width':a:width,
        \'height':a:height,
        \'style':'minimal',
        \'border':'rounded',
        \'title':a:title,
        \'title_pos':'center'})
  return s:float_buf_nr
endfunction

