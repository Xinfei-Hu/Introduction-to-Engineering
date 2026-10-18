from safety.core.agent_core.datamodels import TaskMemory
from safety.core.agent_core.logger import PipelineLogger

class MediaPreprocessAgent:
    """
    媒体预处理智能体，流水线入口Agent
    职责：
    task_type=image：把原图作为唯一帧，填充frame_paths、frame_timestamps
    task_type=video：调用video_frame_extract工具抽帧，写入task_memory帧列表和时间戳
    """
    name = "MediaPreprocessAgent"

    def __init__(self, tool_registry, logger: PipelineLogger):
        self.tool_registry = tool_registry
        self.logger = logger

    def run(self, task_memory: TaskMemory, **kwargs):
        media_path = task_memory.input_path
        output_frame_dir = kwargs.get('output_frame_dir')

        self.logger.info(f'[媒体预处理 Agent] 开始执行：task id：{task_memory.task_id}')
        if task_memory.task_type == 'image':
            self.logger.info('[媒体预处理 Agent] 任务类型: 图片')
            task_memory.frame_paths = [media_path]
            task_memory.frame_timestamps = [0.0]

        elif task_memory.task_type == 'video':
            self.logger.info('[媒体预处理 Agent] 任务类型: 视频')
            self.tool_registry.call(
                tool_name='video_extract_tool',
                agent_name=self.name,
                task_memory=task_memory,
                sample_interval_sec=2.0,
                output_frame_dir=output_frame_dir
            )
            self.logger.info(f'[媒体预处理 Agent] 抽帧完成，总帧数 = {len(task_memory.frame_paths)}')
            if len(task_memory.frame_paths) == 0:
                self.logger.error(f'[媒体预处理 Agent] 视频抽帧结果为空，视频文件可能损坏')
        else:
            self.logger.error(f'[媒体预处理 Agent] 不支持的task_type:{task_memory.task_type}')
            raise Exception(f'不支持的task_type:{task_memory.task_type}')
