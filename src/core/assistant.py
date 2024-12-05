"""
AI助手核心类
"""

import logging
import io
from typing import Dict, Any
import sounddevice as sd
import numpy as np
from pydub import AudioSegment

from audio.wake_word.detector import WakeWordDetector
from llm.base import BaseLLM
from audio.tts.base import BaseTTSEngine
from audio.stt.base import BaseSTTEngine
from skills.registry import ToolRegistry

logger = logging.getLogger(__name__)

class Assistant:
    """AI助手核心类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化助手
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.wake_detector = None
        self.llm = None
        self.tts = None
        self.stt = None
        self.tool_registry = ToolRegistry()
        self.is_listening = False
        self.is_speaking = False
        self.text_buffer = ""
        
    async def initialize(self) -> None:
        """初始化组件"""
        # 初始化唤醒检测
        self.wake_detector = WakeWordDetector(
            porcupine_access_key=self.config['wake_word']['porcupine']['access_key'],
            **self.config['wake_word']['vad']
        )
        
        # 初始化其他组件
        # TODO: 使用工厂模式初始化LLM、TTS、STT
        
    async def start(self) -> None:
        """启动助手"""
        logger.info("正在启动助手...")
        await self.initialize()
        await self.wake_detector.start_detection(self.on_wake_word)
        logger.info("助手已启动")
        
    async def stop(self) -> None:
        """停止助手"""
        logger.info("正在停止助手...")
        if self.wake_detector:
            await self.wake_detector.stop_detection()
        logger.info("助手已停止")
        
    async def on_wake_word(self) -> None:
        """
        唤醒词检测回调
        """
        if not self.is_listening:
            self.is_listening = True
            try:
                await self.process_interaction()
            finally:
                self.is_listening = False
                
    def _is_complete_sentence(self, text: str) -> bool:
        """
        判断是否是完整的句子
        
        Args:
            text: 要判断的文本
            
        Returns:
            是否是完整的句子
        """
        return any(text.endswith(p) for p in '.。!！?？\n')
                
    async def process_interaction(self) -> None:
        """
        处理一次完整的交互
        """
        try:
            # 1. 语音识别
            text = await self.stt.speech_to_text()
            if not text:
                return
                
            # 2. LLM处理
            response_stream = await self.llm.chat_stream(
                messages=[{"role": "user", "content": text}],
                functions=self.tool_registry.get_schemas()
            )
            
            # 3. 处理LLM响应流
            self.text_buffer = ""
            async for text_chunk in response_stream:
                self.text_buffer += text_chunk
                
                # 当积累到完整的句子时进行转换和播放
                if self._is_complete_sentence(self.text_buffer):
                    # 转换文本到语音
                    audio_data = await self.tts.text_to_speech(self.text_buffer)
                    
                    # 播放音频
                    await self._play_audio(audio_data)
                    
                    # 清空缓冲区
                    self.text_buffer = ""
            
            # 处理剩余的文本
            if self.text_buffer:
                audio_data = await self.tts.text_to_speech(self.text_buffer)
                await self._play_audio(audio_data)
                
        except Exception as e:
            logger.error(f"交互处理错误: {e}", exc_info=True)
            # TODO: 播放错误提示音
            
    async def _play_audio(self, audio_data: bytes) -> None:
        """
        播放音频数据
        
        Args:
            audio_data: MP3格式的音频数据
        """
        try:
            # 设置播放状态
            self.is_speaking = True
            
            # 将MP3数据转换为AudioSegment
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # 转换为numpy数组
            samples = np.array(audio_segment.get_array_of_samples())
            
            # 如果是立体声，转换为单声道
            if audio_segment.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)
            
            # 将样本值标准化到[-1, 1]范围
            samples = samples.astype(np.float32)
            samples /= np.iinfo(np.int16).max
            
            # 播放音频
            sd.play(samples, audio_segment.frame_rate)
            sd.wait()  # 等待播放完成
            
        except Exception as e:
            logger.error(f"音频播放错误: {e}", exc_info=True)
        finally:
            # 重置播放状态
            self.is_speaking = False
