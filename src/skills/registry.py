"""
工具注册中心
"""

import logging
from typing import Dict, Type, List, Any
from .base import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """工具注册中心"""
    
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]):
        """
        注册工具类
        
        Args:
            tool_class: 工具类
            
        Returns:
            工具类（用于装饰器）
        """
        cls._tools[tool_class.name] = tool_class
        logger.info(f"注册工具: {tool_class.name}")
        return tool_class
        
    @classmethod
    def get_schemas(cls) -> List[Dict[str, Any]]:
        """
        获取所有工具的schema
        
        Returns:
            工具schema列表
        """
        return [tool.get_schema() for tool in cls._tools.values()]
        
    @classmethod
    async def execute_tool(cls, tool_name: str, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
            
        Raises:
            ValueError: 工具不存在
        """
        if tool_name not in cls._tools:
            raise ValueError(f"工具不存在: {tool_name}")
            
        tool = cls._tools[tool_name]()
        logger.info(f"执行工具: {tool_name}")
        return await tool.execute(**kwargs)
