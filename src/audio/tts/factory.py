"""
TTS 引擎工厂
"""

import logging
from typing import Dict, Any, Type
from .base import BaseTTSEngine
from .edge_tts import EdgeTTSEngine
from .openai_tts import OpenAITTSEngine

logger = logging.getLogger(__name__)

class TTSFactory:
    """TTS 引擎工厂"""
    
    # 注册可用的引擎
    _engines: Dict[str, Type[BaseTTSEngine]] = {
        "edge": EdgeTTSEngine,
        "openai": OpenAITTSEngine
    }
    
    @classmethod
    def create_engine(cls, config: Dict[str, Any]) -> BaseTTSEngine:
        """
        创建 TTS 引擎实例
        
        Args:
            config: TTS配置字典
            
        Returns:
            TTS引擎实例
            
        Raises:
            ValueError: 引擎类型不支持或配置无效
        """
        engine_type = config.get("type")
        if not engine_type:
            raise ValueError("未指定TTS引擎类型")
            
        if engine_type not in cls._engines:
            raise ValueError(f"不支持的TTS引擎类型: {engine_type}")
            
        engine_class = cls._engines[engine_type]
        engine_config = config.get(engine_type, {})
        
        try:
            # 根据引擎类型创建实例
            if engine_type == "edge":
                return engine_class(
                    voice=engine_config.get("voice", "zh-CN-XiaoxiaoNeural")
                )
            elif engine_type == "openai":
                if "api_key" not in engine_config:
                    raise ValueError("OpenAI TTS引擎需要提供api_key")
                return engine_class(
                    api_key=engine_config["api_key"],
                    api_base=engine_config.get("api_base"),
                    voice=engine_config.get("voice", "alloy"),
                    model=engine_config.get("model", "tts-1")
                )
            else:
                # 对于自定义引擎，使用配置字典作为参数
                return engine_class(**engine_config)
                
        except Exception as e:
            logger.error(f"创建TTS引擎失败: {e}", exc_info=True)
            raise
            
    @classmethod
    def register_engine(cls, engine_type: str, engine_class: Type[BaseTTSEngine]) -> None:
        """
        注册新的引擎类型
        
        Args:
            engine_type: 引擎类型名称
            engine_class: 引擎类
        """
        if not issubclass(engine_class, BaseTTSEngine):
            raise ValueError(f"引擎类 {engine_class.__name__} 必须继承 BaseTTSEngine")
            
        cls._engines[engine_type] = engine_class
        logger.info(f"注册TTS引擎: {engine_type} -> {engine_class.__name__}")
