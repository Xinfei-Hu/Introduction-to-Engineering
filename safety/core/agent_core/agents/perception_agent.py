# safety/core/agent_core/agents/perception_agent.py
# 感知 AGENT
# 只做视觉提取。不做风险研判

from safety.core.agent_core.datamodels import TaskMemory, PerceptionResult
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.logger import PipelineLogger

class PerceptionAgent:
    """感知智能体：只做视觉证据提取，不做风险研判"""
    name = "PerceptionAgent"

    def __init__(self, tool_registry: ToolRegistry, logger: PipelineLogger):
        self.tool_registry = tool_registry
        self.logger = logger

    def run(self, task_memory: TaskMemory, **kwargs) -> PerceptionResult:
        self.logger.info(f'\n------ [感知 Agent 开始执行] task id：{task_memory.task_id} ------')
        input_path = task_memory.input_path
        task_type = task_memory.task_type

        if task_type == 'image':
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
                frame_time=None,
                tool_records=task_memory.all_tool_logs[-1:]
            )
        elif task_type == 'video':
                # 视频任务：后续开发
                raise NotImplementedError('视频功能待开发')
        else:
            raise ValueError(f'不支持的任务类型:{task_type}')

        self.logger.info(f'感知 Agent 完成, 检测到目标数量：{len(perception_result.bboxes)}')
        # 出入历史记录
        task_memory.perception_history.append(perception_result)
        return perception_result