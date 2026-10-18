# safety/core/agent_core/agents/perception_agent.py
# 感知 AGENT
# 只做视觉提取，不做风险研判

from safety.core.agent_core.datamodels import TaskMemory, PerceptionResult
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.logger import PipelineLogger

class PerceptionAgent:
    """感知智能体：只做视觉证据提取，不做风险研判"""
    name = "PerceptionAgent"

    def __init__(self, tool_registry: ToolRegistry, logger: PipelineLogger): # 修改：新增logger参数
        self.tool_registry = tool_registry
        self.logger = logger  # 修改：新增实例变量

    def run(self, task_memory: TaskMemory, **kwargs) -> PerceptionResult:
        self.logger.info(f'[感知 Agent] 开始执行：task id：{task_memory.task_id}')
        input_path = getattr(task_memory, 'current_frame_path', task_memory.input_path)
        frame_time = getattr(task_memory, 'current_frame_time', None)



        # 图片任务，直接调用 yolo_detect
        save_mark_path = kwargs.get('save_mark_path')
        tool_result = self.tool_registry.call(
            tool_name='yolo_detect',
            agent_name=self.name,
            task_memory=task_memory,
            image_path=input_path,
            save_mark_path=save_mark_path
        )
        perception_result = PerceptionResult(
            image_path=input_path,
            marked_image_path=tool_result['marked_image_path'],
            bboxes=tool_result['bboxes'],
            raw_text=tool_result['raw_text'],
            frame_time=frame_time,
            tool_records=task_memory.all_tool_logs[-1:]
        )


        self.logger.info(f'[感知 Agent] 完成, 检测到目标数量：{len(perception_result.bboxes)}') # 修改为info日志收集
        # 出入历史记录
        task_memory.perception_history.append(perception_result)
        return perception_result
