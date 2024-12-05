"""
STT基础接口定义
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseSTTEngine(ABC):
    """STT引擎基础接口"""
    
    @abstractmethod
    async def speech_to_text(self, audio_data: Optional[bytes] = None) -> str:
        """
        将语音转换为文本
        
        Args:
            audio_data: 音频数据，如果为None则从录音设备获取
            
        Returns:
            识别出的文本
        """
        pass
