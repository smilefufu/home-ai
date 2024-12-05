"""
TTS引擎性能测试示例
"""

import os
import sys
import asyncio
import time
import logging
from pathlib import Path
import io
import sounddevice as sd
import numpy as np
from pydub import AudioSegment

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.audio.tts.factory import TTSFactory
from src.core.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def play_audio(audio_data: bytes):
    """播放音频数据"""
    try:
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
        logger.info("正在播放音频...")
        sd.play(samples, audio_segment.frame_rate)
        sd.wait()
        logger.info("音频播放完成")
        
    except Exception as e:
        logger.error(f"播放音频失败: {e}", exc_info=True)

async def test_tts_performance():
    """测试TTS引擎性能"""
    # 加载配置
    config_path = Path(project_root) / "config" / "config.example.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    logger.info(f"使用配置文件: {config_path}")
    config = load_config(config_path)
    
    # 创建TTS引擎
    tts_config = config["tts"]
    logger.info(f"TTS引擎配置: {tts_config}")
    engine = TTSFactory.create_engine(tts_config)
    
    # 测试文本
    test_texts = [
        "你好，我是一个AI助手。",
        "你好！",
        "今天天气真不错，阳光明媚。",
        "让我们来测试一下TTS引擎的性能。",
        "这是一个较长的句子，包含了更多的文字内容，用于测试TTS引擎处理长文本的性能表现。"
    ]
    
    total_time = 0
    total_size = 0
    last_audio_data = None
    
    # 测试每个文本
    for text in test_texts:
        start_time = time.time()
        
        try:
            # 转换文本到语音
            audio_data = await engine.text_to_speech(text)
            last_audio_data = audio_data  # 保存最后一个音频数据
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 计算音频大小（KB）
            size_kb = len(audio_data) / 1024
            total_size += size_kb
            total_time += duration
            
            logger.info(f"文本: {text}")
            logger.info(f"处理时间: {duration:.2f}秒")
            logger.info(f"音频大小: {size_kb:.2f}KB")
            logger.info("-" * 50)
        except Exception as e:
            logger.error(f"处理文本时出错: {text}")
            logger.error(f"错误信息: {str(e)}")
            raise
    
    # 输出总体统计
    avg_time = total_time / len(test_texts)
    avg_size = total_size / len(test_texts)
    logger.info(f"性能统计:")
    logger.info(f"平均处理时间: {avg_time:.2f}秒")
    logger.info(f"平均音频大小: {avg_size:.2f}KB")
    logger.info(f"总处理时间: {total_time:.2f}秒")
    logger.info(f"总音频大小: {total_size:.2f}KB")
    
    # 播放最后一条文本的音频
    if last_audio_data:
        logger.info(f"\n播放最后一条文本的音频: {test_texts[-1]}")
        play_audio(last_audio_data)

if __name__ == "__main__":
    try:
        asyncio.run(test_tts_performance())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
