"""调用大模型"""
from safety.core.agent_core.tool_registry import BaseTool
from safety.core.agent_core.datamodels import TaskMemory
from safety.core.api.llm_vision_api import DoubaoVisionClient

class LlmVisonAnalyzeTool(BaseTool):
    name = 'llm_vision_analyze'
    description = '调用豆包多模态大模型，结果图片和上下文，分析工地安全隐患'

    def __init__(self):
        self.client = DoubaoVisionClient()

    def run(self, task_memory: TaskMemory, **kwargs) -> dict:
        image_path = kwargs.get("image_path")
        prompt = kwargs.get("prompt")
        result = self.client.analyze_image(image_path, prompt)
        return result