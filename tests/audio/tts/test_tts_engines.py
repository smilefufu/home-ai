"""
TTS 引擎测试
"""

import os
import sys
import logging
import pytest

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from src.audio.tts.factory import TTSFactory
from src.audio.tts.base import BaseTTSEngine

logger = logging.getLogger(__name__)

# 设置默认的事件循环作用域为函数级别
pytestmark = pytest.mark.asyncio(scope="function")

@pytest.fixture
def edge_config():
    """Edge TTS 配置"""
    return {
        "type": "edge",
        "edge": {
            "voice": "zh-CN-XiaoxiaoNeural"
        }
    }

@pytest.fixture
def openai_config():
    """OpenAI TTS 配置"""
    return {
        "type": "openai",
        "openai": {
            "api_key": "test_key",
            "api_base": "http://localhost:5050/v1",
            "voice": "alloy",
            "model": "tts-1"
        }
    }

@pytest.mark.asyncio
async def test_edge_tts_creation(edge_config):
    """测试 Edge TTS 创建"""
    engine = TTSFactory.create_engine(edge_config)
    assert engine is not None
    logger.info("Edge TTS 创建成功")

@pytest.mark.asyncio
async def test_openai_tts_creation(openai_config):
    """测试 OpenAI TTS 创建"""
    engine = TTSFactory.create_engine(openai_config)
    assert engine is not None
    logger.info("OpenAI TTS 创建成功")

@pytest.mark.asyncio
async def test_edge_tts_conversion(edge_config):
    """测试 Edge TTS 文本转换"""
    engine = TTSFactory.create_engine(edge_config)
    text = "你好，世界"
    
    # 转换文本
    audio_data = await engine.text_to_speech(text)
    
    # 验证结果
    assert isinstance(audio_data, bytes)
    assert len(audio_data) > 0
    logger.info(f"Edge TTS 转换成功，音频大小: {len(audio_data)} 字节")

@pytest.mark.asyncio
async def test_invalid_engine_type():
    """测试无效的引擎类型"""
    config = {
        "type": "invalid",
        "invalid": {}
    }
    
    with pytest.raises(ValueError, match="不支持的TTS引擎类型"):
        TTSFactory.create_engine(config)
    logger.info("无效引擎类型测试通过")

@pytest.mark.asyncio
async def test_missing_engine_type():
    """测试缺少引擎类型"""
    config = {}
    
    with pytest.raises(ValueError, match="未指定TTS引擎类型"):
        TTSFactory.create_engine(config)
    logger.info("缺少引擎类型测试通过")

@pytest.mark.asyncio
async def test_missing_api_key(openai_config):
    """测试缺少API密钥"""
    openai_config["openai"].pop("api_key", None)
    
    with pytest.raises(ValueError, match="OpenAI TTS引擎需要提供api_key"):
        TTSFactory.create_engine(openai_config)
    logger.info("缺少API密钥测试通过")

@pytest.mark.asyncio
async def test_engine_registration():
    """测试引擎注册"""
    # 创建测试引擎类
    class TestEngine(BaseTTSEngine):
        async def text_to_speech(self, text: str) -> bytes:
            return b"test_audio_data"
    
    # 注册测试引擎
    TTSFactory.register_engine("test", TestEngine)
    
    # 创建测试引擎实例
    config = {
        "type": "test",
        "test": {}
    }
    engine = TTSFactory.create_engine(config)
    
    assert isinstance(engine, TestEngine)
    logger.info("引擎注册测试通过")
