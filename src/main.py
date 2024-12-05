#!/usr/bin/env python3
"""
Home AI Assistant
主程序入口
"""

import asyncio
import logging
from pathlib import Path
from core.assistant import Assistant
from core.config import load_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主程序入口"""
    try:
        # 加载配置
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        config = load_config(config_path)
        
        # 初始化助手
        assistant = Assistant(config)
        
        # 启动助手
        await assistant.start()
        
        # 保持程序运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("正在关闭助手...")
        if 'assistant' in locals():
            await assistant.stop()
        logger.info("助手已关闭")
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)
        
if __name__ == "__main__":
    asyncio.run(main())
