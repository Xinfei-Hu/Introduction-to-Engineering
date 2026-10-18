from pathlib import Path
from safety.core.agent_core.datamodels import TaskMemory
from safety.core.tools.yolo_tool import YoloDetectTool
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.agents.perception_agent import PerceptionAgent
from safety.core.agent_core.logger import PipelineLogger
# 新增导包
from safety.core.tools.rule_tool import RuleRetrievalTool
from safety.core.tools.llm_vision_tool import LlmVisonAnalyzeTool
from safety.core.agent_core.agents.risk_analyze_agent import RiskAnalyzeAgent

def run_pipeline(media_path: str | Path, task_type: str = 'image'):

    # 日志记录实例
    logger = PipelineLogger()

    # 实例化工具注册器
    registry = ToolRegistry(logger)

    # 实例化工具并注册
    # 下面两行该为一行 registry.register(YoloDetectTool())
    # yolo_detect_tool = YoloDetectTool()
    # registry.register(yolo_detect_tool)
    registry.register(YoloDetectTool())
    registry.register(RuleRetrievalTool())
    registry.register(LlmVisonAnalyzeTool())



    mem = TaskMemory.create_new_task(media_path, 'image')
    # 1. 运行感知
    p_agent = PerceptionAgent(registry, logger)
    p_agent.run(mem, image_path=media_path, save_mark_path='./output/mark_image.jpg')

    # 2. 再研判
    a_agent = RiskAnalyzeAgent(registry, logger)
    res = a_agent.run(mem)

    print('------ 研判结果 ------')
    for h in res.hazard_list:
        print(f'隐患类型: {h.danger_type}， 等级：{h.risk_level} ，描述：: {h.description}')


if __name__ == '__main__':
    # 图片测试
    media_path = './media/image/test.jpg'
    task_type = 'image'
    run_pipeline(media_path, task_type)