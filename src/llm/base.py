"""
LLM基础接口定义
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional

class BaseLLM(ABC):
    """LLM基础接口"""
    
    @abstractmethod
    async def chat_stream(self,
                         messages: List[Dict[str, str]],
                         functions: Optional[List[Dict[str, Any]]] = None) -> AsyncIterator[str]:
        """
        流式对话
        
        Args:
            messages: 对话历史
            functions: 可用的函数列表
            
        Yields:
            响应文本流
        """
        pass
        
    @abstractmethod
    async def chat(self,
                  messages: List[Dict[str, str]],
                  functions: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        完整对话
        
        Args:
            messages: 对话历史
            functions: 可用的函数列表
            
        Returns:
            完整响应文本
        """
        pass
