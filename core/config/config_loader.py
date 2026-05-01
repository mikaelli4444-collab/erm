import yaml
import os
from dotenv import load_dotenv
from typing import Callable, Any, TypeAlias
from types import SimpleNamespace
from pathlib import Path

load_dotenv()

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"

def resolve_env(value):
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        env_value = os.getenv(env_var)

        if env_value is None:
            raise ValueError(f"Environment variable '{env_var}' is not set")

        return env_value

    return value

def to_obj(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{
            k: to_obj(resolve_env(v)) for k, v in d.items()
        })
    return resolve_env(d)

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

def parse_property(property: str, parser: Callable[[str | None], "ParseConfigResult"]):
    property = property.removeprefix('.')
    
    attrs = property.split(".")
    value = RAW_CONFIG
    for attr in attrs:
        value = getattr(value, attr, None)
    
    success, error, result = parser(value)

    if not success:
        raise ValueError(f"The config {property} is invalid\n{error}")

    return result