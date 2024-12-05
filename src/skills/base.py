"""
工具基础类定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, ClassVar

class BaseTool(ABC):
    """工具基础类"""
    
    name: ClassVar[str]  # 工具名称
    description: ClassVar[str]  # 工具描述
    parameters: ClassVar[Dict[str, Any]]  # 参数模式
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        获取工具的schema
        
        Returns:
            符合OpenAI Function Calling格式的schema
        """
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": cls.parameters,
                "required": [k for k, v in cls.parameters.items() 
                           if v.get("required", False)]
            }
        }
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
        """
        pass
