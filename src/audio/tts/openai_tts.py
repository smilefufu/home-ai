"""
OpenAI TTS 引擎实现
"""

import logging
import asyncio
from typing import AsyncIterator, Union
from openai import AsyncOpenAI
from .base import BaseTTSEngine

logger = logging.getLogger(__name__)

class OpenAITTSEngine(BaseTTSEngine):
    """OpenAI TTS 引擎"""
    
    def __init__(self, 
                 api_key: str,
                 api_base: str = None,
                 voice: str = "alloy",
                 model: str = "tts-1"):
        """
        初始化 OpenAI TTS 引擎
        
        Args:
            api_key: OpenAI API密钥
            api_base: API基础URL（可选，用于兼容接口）
            voice: 语音名称
            model: 模型名称
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.voice = voice
        self.model = model
        
    @property
    def supports_streaming(self) -> bool:
        """是否支持流式处理"""
        return False
        
    async def text_to_speech_stream(self, text_iterator: AsyncIterator[str]) -> AsyncIterator[bytes]:
        """
        将文本流转换为语音流
        
        由于OpenAI TTS不支持真正的流式处理，这里我们会等待收集完整的文本后再处理
        
        Args:
            text_iterator: 文本流迭代器
            
        Yields:
            音频数据块
        """
        # 收集完整文本
        text_chunks = []
        async for chunk in text_iterator:
            text_chunks.append(chunk)
        text = ''.join(text_chunks)
        
        # 转换为语音
        try:
            audio_data = await self.text_to_speech(text)
            
            # 分块返回
            chunk_size = 1024 * 16  # 16KB chunks
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
                
        except Exception as e:
            logger.error(f"OpenAI TTS 转换错误: {e}", exc_info=True)
            raise
            
    async def text_to_speech(self, text: str) -> bytes:
        """
        将完整文本转换为语音
        
        Args:
            text: 要转换的文本
            
        Returns:
            音频数据
        """
        try:
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            
            # response.read() 已经返回 bytes，不需要 await
            return response.read()
            
        except Exception as e:
            logger.error(f"OpenAI TTS 转换错误: {e}", exc_info=True)
            raise
