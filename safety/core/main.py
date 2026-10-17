from webbrowser import register

from safety.core.agent_core.datamodels import TaskMemory
from safety.core.tools.yolo_tool import YoloDetectTool
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.agents.perception_agent import PerceptionAgent

def run_pipeline(media_path: str):
    registry = ToolRegistry()
    yolo_detect_tool = YoloDetectTool()
    registry.register(yolo_detect_tool)
    mem = TaskMemory.create_new_task(media_path, 'image')

    p_agent = PerceptionAgent(registry)
    res = p_agent.run(mem, image_path = media_path, save_mark_path='./output/mark_image.jpg')

    print(res.raw_text)
    print(mem.all_tool_logs[0])

if __name__ == '__main__':
    media_path = './media/images/test.jpg'
    run_pipeline(media_path)