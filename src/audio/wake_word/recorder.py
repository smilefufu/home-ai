"""
音频录制模块
"""

import logging
from typing import AsyncIterator
import pyaudio
import asyncio

logger = logging.getLogger(__name__)

class AudioRecorder:
    """音频录制器"""
    
    def __init__(self,
                 sample_rate: int = 16000,
                 chunk_size: int = 480,
                 channels: int = 1,
                 format: int = pyaudio.paInt16):
        """
        初始化录音器
        
        Args:
            sample_rate: 采样率
            chunk_size: 块大小
            channels: 通道数
            format: 音频格式
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format = format
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self._running = False
        
    async def start_recording(self) -> AsyncIterator[bytes]:
        """
        开始录音
        
        Yields:
            音频数据块
        """
        logger.info("开始录音...")
        self._running = True
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self._running:
                if self.stream.is_active():
                    # 使用事件循环执行阻塞操作
                    data = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.stream.read,
                        self.chunk_size
                    )
                    yield data
                else:
                    break
                    
        except Exception as e:
            logger.error(f"录音错误: {e}", exc_info=True)
            raise
        finally:
            await self.stop_recording()
            
    async def stop_recording(self) -> None:
        """停止录音"""
        logger.info("停止录音...")
        self._running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if self.audio:
            self.audio.terminate()
            self.audio = None
