"""
TTS 引擎基类
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class BaseTTSEngine:
    """TTS 引擎基类"""
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            
        Returns:
            音频数据（MP3格式）
        """
        raise NotImplementedError
