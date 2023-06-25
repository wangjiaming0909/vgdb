## What is VGDB?

VGDB is a nvim plugin for gdb debuging. vim is not supported now.  
VGDB is a wrapper of gdb, start gdb with cmd: `--interpreter=mi3`.  

## How to use?
Install plugin:
```vimscript
Plug 'wangjiaming0909/vgdb'
```
```sh
pip3 install pygdbmi
```

Add a command map to VGDB_Start() in you init.vim
```vimscript
nnoremap <F5> :call VGDB_Start()<CR>
```
