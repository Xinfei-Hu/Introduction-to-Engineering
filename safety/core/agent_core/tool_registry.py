from abc import ABC
from typing import Dict, Any
from safety.core.agent_core.datamodels import TaskMemory, ToolCallRecord

class BaseTool(ABC):
    """工具抽象类"""
    name: str
    description: str

    def run(self, task_memory:TaskMemory, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Tool must implement run()")

class ToolRegistry:
    "工具注册器"
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool
        print(f'[Register Tool] Tool name: {tool.name}')

    def call(self, tool_name: str, agent_name: str, task_memory: TaskMemory, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f'Tool {tool_name} not registered')
        tool = self.tools[tool_name]
        print(f'[Call Tool] Tool name: {tool.name}')
        result = tool.run(task_memory, **kwargs)
        log = ToolCallRecord(
                agent_name = agent_name,
                tool_name = tool_name,
                input_args = kwargs,
                output = result)

        task_memory.all_tool_logs.append(log)
        return result