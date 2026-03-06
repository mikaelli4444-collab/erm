
import yaml
import os

from typing import Callable, Any, TypeAlias
from types import SimpleNamespace
from pathlib import Path

CONFIG_PATH = Path(os.path.dirname(__file__)) / '..' / '..' / 'config.yaml'

def to_obj(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{
            k: to_obj(v) for k, v in d.items()
        })
    return d

with open(CONFIG_PATH, 'r', encoding='utf8') as config_file:
    config_raw_dict = yaml.safe_load(config_file.read())
    RAW_CONFIG = to_obj(config_raw_dict)

ParseConfigResult: TypeAlias = tuple[bool, str|None, Any]
"""
Map: 
    0 - success
    1 - error
    2 - result
"""

def parse_property(property:str, parser:Callable[[str|None], ParseConfigResult]):
    
    property.removeprefix('.')

    value = eval(f'RAW_CONFIG.{property}') #esta linea
    success, error, result = parser(value)

    if not success:
        raise ValueError(f'The config {property} is invalid\n{error}')

    return result
