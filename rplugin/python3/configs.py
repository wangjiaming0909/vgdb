import configparser
import os.path

config_file = os.path.expanduser('~') + '/.config/vdb/vdb.conf'

configs: configparser.ConfigParser = None

def reload_configs() -> configparser.ConfigParser:
    global configs
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    configs = config_parser
    return configs

def get_config(o: str) -> str:
    global configs
    if configs is None:
        reload_configs()
    return configs[configs.default_section][o]

def get_sec_config(sec: str, o: str) -> str:
    global configs
    if configs is None:
        reload_configs()
    return configs[sec][o]

def has_config(o: str) -> str:
    global configs
    if configs is None:
        reload_configs()
    return o in configs[configs.default_section]

if __name__ == '__main__':
    cfs = reload_configs()
    for o in cfs[cfs.default_section]:
        print(cfs.default_section + '.' + o + '.' + cfs.get(cfs.default_section, o))
    for sec in cfs.sections():
        for o in cfs.options(sec):
            print(sec + '.' + o + '.' + cfs.get(sec, o))
    
    print(get_sec_config('DEFAULT', 'dbg'))
    print(get_config('dbg'))