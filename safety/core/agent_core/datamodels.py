from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import uuid


@dataclass
class BBox:
    """YOLO检测框，目标位置信息"""
    cls_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class ToolCallRecord:
    """工具调用日志记录"""
    agent_name: str
    tool_name: str
    input_args: Dict[str, Any]
    output: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    note: str = ""


@dataclass
class PerceptionResult:
    """感知Agent输出结果"""
    image_path: str
    marked_image_path: str
    bboxes: List[BBox]
    raw_text: str
    frame_time: Optional[float] = None
    tool_records: List[ToolCallRecord] = field(default_factory=list)


@dataclass
class SingleHazard:
    """单条隐患"""
    danger_type: str
    description: str
    risk_level: str  # 高 / 中 / 低
    evidence: str
    suggestion: str
    bbox_ref: Optional[BBox] = None
    uncertainty: str = ""


@dataclass
class RiskAnalyzeResult:
    """风险研判Agent输出"""
    hazard_list: List[SingleHazard] = field(default_factory=list)
    has_danger: bool = False
    uncertainty_global: str = ""
    tool_records: List[ToolCallRecord] = field(default_factory=list)


@dataclass
class ReviewResult:
    """复核Agent输出"""
    final_hazard_list: List[SingleHazard]
    has_danger: bool
    is_conflict: bool
    conflict_message: str
    uncertainty_global: str
    tool_records: List[ToolCallRecord] = field(default_factory=list)


@dataclass
class TaskMemory:
    """短期任务记忆，单次检测任务上下文"""
    task_id: str
    input_path: str
    task_type: str  # image / video
    iteration_count: int = 0
    max_iter: int = 2
    perception_history: List[PerceptionResult] = field(default_factory=list)
    analyze_history: List[RiskAnalyzeResult] = field(default_factory=list)
    review_history: List[ReviewResult] = field(default_factory=list)
    all_tool_logs: List[ToolCallRecord] = field(default_factory=list)

    # ---------- 媒体帧相关字段 -------------
    frame_paths: List[str] = field(default_factory=list)  # 所有帧图片路径列表
    frame_timestamps: List[float] = field(default_factory=list)  # 对应帧的时间戳
    current_frame_path: str = ""  # 当前正在处理的帧图片路径
    current_frame_time: float = 0.0  # 当前对应的视频时间

    @staticmethod
    def create_new_task(input_path: str, task_type: str, max_iter: int = 2):
        task_id = str(uuid.uuid4())
        return TaskMemory(
            task_id=task_id,
            input_path=input_path,
            task_type=task_type,
            max_iter=max_iter
        )


@dataclass
class HumanFeedbackCase:
    """长期记忆：人工反馈案例（暂时预留，后期实现）"""
    case_id: str
    image_path: str
    origin_hazard_list: List[SingleHazard]
    corrected_hazard_list: List[SingleHazard]
    feedback_note: str
    create_time: str