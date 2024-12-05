"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: 配置文件格式错误
    """
    # 加载环境变量
    load_dotenv()
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 处理环境变量
    _process_env_vars(config)
    
    return config

def _process_env_vars(config: Dict[str, Any]) -> None:
    """
    处理配置中的环境变量引用
    
    Args:
        config: 配置字典
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var)
            elif isinstance(value, (dict, list)):
                _process_env_vars(value)
    elif isinstance(config, list):
        for i, value in enumerate(config):
            if isinstance(value, (dict, list)):
                _process_env_vars(value)
