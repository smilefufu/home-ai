"""
Edge TTS 引擎实现
"""

import logging
import edge_tts
from .base import BaseTTSEngine

logger = logging.getLogger(__name__)

class EdgeTTSEngine(BaseTTSEngine):
    """Edge TTS 引擎"""
    
    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz"):
        """
        初始化 Edge TTS 引擎
        
        Args:
            voice: 语音名称
            rate: 语速，如 "+50%"、"-20%"
            volume: 音量，如 "+50%"、"-20%"
            pitch: 音调，如 "+10Hz"、"-10Hz"
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        
    async def text_to_speech(self, text: str) -> bytes:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            
        Returns:
            音频数据（MP3格式）
        """
        try:
            communicate = edge_tts.Communicate(
                text, 
                self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )
            audio_data = bytearray()
            
            async for chunk in communicate.stream():
                # 只处理音频数据
                if isinstance(chunk, dict) and chunk.get("type") == "audio":
                    audio_data.extend(chunk["data"])
                
            return bytes(audio_data)
            
        except Exception as e:
            logger.error(f"Edge TTS 转换错误: {e}", exc_info=True)
            raise
