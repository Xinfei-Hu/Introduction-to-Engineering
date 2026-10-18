import cv2
from pathlib import Path
from safety.core.agent_core.datamodels import TaskMemory
from safety.core.agent_core.tool_registry import BaseTool

class VideoFrameExtractTool(BaseTool):
    """视频抽帧工具"""
    name = 'video_extract_tool'
    description = '视频抽帧工具：输入视频路径，按指定时间间隔提取帧图片，写入task memory帧列表与时间戳'

    def run(self, task_memory: TaskMemory, sample_interval_sec: float = 2.0, **kwargs):
        if sample_interval_sec <= 0:
            raise ValueError('sample_interval_sec 必须大于 0')

        video_path = task_memory.input_path
        output_frame_dir = kwargs.get('output_frame_dir')
        output_frame_dir = Path(output_frame_dir) / task_memory.task_id
        output_frame_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        try:
            if not cap.isOpened():
                raise Exception(f'视频打开失败:{video_path}')

            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <=0:
                cap.release()
                raise Exception('读取视频FPS失败')

            frame_step = int(fps * sample_interval_sec)
            frame_paths = []
            timestamps = []
            idx = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if idx % frame_step == 0:
                    current_sec = idx / fps
                    frame_name = f'frame_{idx}_{current_sec:.2f}.jpg'
                    save_path = str(output_frame_dir / frame_name)
                    cv2.imwrite(save_path, frame)
                    frame_paths.append(save_path)
                    timestamps.append(current_sec)
                idx += 1
            cap.release()

            task_memory.frame_paths = frame_paths
            task_memory.frame_timestamps = timestamps

            return {
                'frame_count': len(frame_paths),
                'frame_list': frame_paths,
                'time_list': timestamps,
            }
        finally:
            cap.release()