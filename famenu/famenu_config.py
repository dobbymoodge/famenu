from collections import OrderedDict
import shlex
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import re


def split_key_value_line(line):
    chunks = shlex.split(line, True)
    if len(chunks) == 0:
        return None, None
    div = chunks.index('=')
    key = ' '.join(chunks[:div])
    value = chunks[div + 1:]
    return key, value


def split_value_line(line):
    chunks = shlex.split(line.strip(), True)
    return chunks


def parse_config_file_tokens(cfgfile):
    last_tok_type = ''
    value = ''
    key = ''
    for line in cfgfile:
        if last_tok_type == 'value':
            if re.search(r'^\s+', line):
                line = line.strip()
                if len(line) > 0:
                    value += split_value_line(line)
                continue
            else:
                if value is not None:
                    yield ('value', value)
        last_tok_type = ''
        line = line.strip()
        if len(line) > 0:
            if line[0] == '[' and line[-1] == ']':
                section_name = line[1:-1]
                if section_name == 'config':
                    yield ('config', line[1:-1])
                else:
                    yield ('cfg_section', line[1:-1])
            else:
                key, value = split_key_value_line(line)
                if key is not None:
                    yield ('key', key)
                last_tok_type = 'value'


def parse_config_filestream(cfgfile):
    config = {}
    cfg_section = ""
    cfg_key = ""
    for token_type, token in parse_config_file_tokens(cfgfile):
        if token_type == 'config':
            cfg_section = 'config'
            config[cfg_section] = OrderedDict()
        elif token_type == 'cfg_section':
            cfg_section = token
            if cfg_section in config:
                raise ValueError(
                    "Config section \"%s\" appears more than once in config" %
                    (cfg_key, cfg_section))
            config[cfg_section] = OrderedDict()
        elif token_type == 'key':
            cfg_key = token
            if cfg_key in config[cfg_section]:
                raise ValueError(
                    "Key \"%s\" duplicated in config section \"%s\"" %
                    (cfg_key, cfg_section))
        elif token_type == 'value':
            config[cfg_section][cfg_key] = token
    return config


def loads(cfg_string):
    cfg_sio = StringIO(cfg_string)
    return parse_config_filestream(cfg_sio)


def load(cfg_file):
    if isinstance(cfg_file, str):
        cf = open(cfg_file, 'r')
    else:
        cf = cfg_file
    return parse_config_filestream(cf)
