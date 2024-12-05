"""
唤醒词检测模块
"""

import logging
from typing import Callable, Optional, List
import webrtcvad
from pvporcupine import Porcupine
from .recorder import AudioRecorder

logger = logging.getLogger(__name__)

class WakeWordDetector:
    """
    基于VAD和Porcupine的双重检测唤醒系统
    """
    
    def __init__(self,
                 porcupine_access_key: str,
                 keywords: List[str] = None,
                 vad_aggressiveness: int = 3,
                 sample_rate: int = 16000,
                 frame_duration_ms: int = 30,
                 speech_pad_ms: int = 300,
                 min_speech_duration_ms: int = 250):
        """
        初始化唤醒词检测器
        
        Args:
            porcupine_access_key: Picovoice访问密钥
            keywords: 唤醒词列表
            vad_aggressiveness: VAD灵敏度(0-3)
            sample_rate: 采样率
            frame_duration_ms: 帧持续时间(ms)
            speech_pad_ms: 语音填充时间(ms)
            min_speech_duration_ms: 最小语音持续时间(ms)
        """
        # VAD配置
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.speech_pad_frames = int(speech_pad_ms / frame_duration_ms)
        self.min_speech_frames = int(min_speech_duration_ms / frame_duration_ms)
        
        # Porcupine配置
        self.porcupine = Porcupine(
            access_key=porcupine_access_key,
            keywords=keywords or ["hey computer"]
        )
        
        # 音频缓冲
        self.audio_buffer = []
        self.speech_frames = 0
        self.silence_frames = 0
        
        # 状态控制
        self.is_speech_active = False
        self._running = False
        
        # 音频录制器
        self.recorder = AudioRecorder(
            sample_rate=sample_rate,
            chunk_size=self.frame_size
        )
        
    async def start_detection(self, on_wake_word: Callable[[], None]) -> None:
        """
        启动检测
        
        Args:
            on_wake_word: 检测到唤醒词时的回调函数
        """
        logger.info("启动唤醒词检测...")
        self._running = True
        
        try:
            async for audio_chunk in self.recorder.start_recording():
                if not self._running:
                    break
                    
                # 1. VAD检测
                is_speech = self.vad.is_speech(audio_chunk, self.sample_rate)
                
                # 2. 状态更新和缓冲处理
                await self._process_audio_state(audio_chunk, is_speech)
                
                # 3. 在语音结束时进行唤醒词检测
                if await self._should_check_wake_word():
                    if await self._check_wake_word():
                        await on_wake_word()
                    self._reset_state()
                    
        except Exception as e:
            logger.error(f"唤醒词检测错误: {e}", exc_info=True)
            raise
            
    async def _process_audio_state(self, audio_chunk: bytes, is_speech: bool) -> None:
        """
        处理音频状态
        
        Args:
            audio_chunk: 音频数据
            is_speech: 是否为语音
        """
        if is_speech:
            self.speech_frames += 1
            self.silence_frames = 0
            if not self.is_speech_active and self.speech_frames >= self.min_speech_frames:
                self.is_speech_active = True
        else:
            self.silence_frames += 1
            if self.silence_frames >= self.speech_pad_frames:
                self.speech_frames = 0
                
        # 维护音频缓冲区
        if self.is_speech_active:
            self.audio_buffer.append(audio_chunk)
            # 限制缓冲区大小
            if len(self.audio_buffer) > 100:  # 约3秒音频
                self._reset_state()
                
    async def _should_check_wake_word(self) -> bool:
        """
        判断是否应该检查唤醒词
        
        Returns:
            是否应该检查唤醒词
        """
        return (self.is_speech_active and 
                self.silence_frames >= self.speech_pad_frames and 
                len(self.audio_buffer) > 0)
                
    async def _check_wake_word(self) -> bool:
        """
        检查唤醒词
        
        Returns:
            是否检测到唤醒词
        """
        try:
            # 合并音频缓冲区
            audio_data = b''.join(self.audio_buffer)
            
            # 确保音频长度符合Porcupine要求
            frame_length = self.porcupine.frame_length
            num_frames = len(audio_data) // frame_length
            
            for i in range(num_frames):
                frame = audio_data[i * frame_length:(i + 1) * frame_length]
                result = self.porcupine.process(frame)
                if result >= 0:
                    logger.info("检测到唤醒词")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"唤醒词检查错误: {e}", exc_info=True)
            return False
            
    def _reset_state(self) -> None:
        """重置状态"""
        self.audio_buffer.clear()
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speech_active = False
        
    async def stop_detection(self) -> None:
        """停止检测"""
        logger.info("停止唤醒词检测...")
        self._running = False
        await self.recorder.stop_recording()
        self.porcupine.delete()
