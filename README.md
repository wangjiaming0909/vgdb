## What is VGDB?

VGDB is a nvim plugin for gdb debuging. vim is not supported now.  
VGDB is a wrapper of gdb, start gdb with cmd: `--interpreter=mi3`.  

## How to use?
Install plugin:
```vimscript
Plug 'skywind3000/vim-quickui'
Plug 'wangjiaming0909/vgdb'
```
Install py package `pygdbmi`
```sh
pip3 install pygdbmi
```
Intall fdfind
```sh
sudo apt install fd-find
```

Add a command map to VGDB_Start() in you init.vim
```vimscript
nnoremap <F5> :call VGDB_Start()<CR>
```
