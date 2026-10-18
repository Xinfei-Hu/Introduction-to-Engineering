from pathlib import Path
from safety.core.agent_core.datamodels import TaskMemory
from safety.core.tools.yolo_tool import YoloDetectTool
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.agents.perception_agent import PerceptionAgent
from safety.core.agent_core.logger import PipelineLogger
from safety.core.tools.rule_tool import RuleRetrievalTool
from safety.core.tools.llm_vision_tool import LlmVisonAnalyzeTool
from safety.core.agent_core.agents.risk_analyze_agent import RiskAnalyzeAgent
from safety.core.agent_core.agents.review_agent import ReviewAgent
from safety.core.agent_core.repository import JsonRuleRepo
from safety.core.agent_core.pdf_exporter import PdfExporter
from safety.core.tools.video_extract_tool import VideoFrameExtractTool
from safety.core.agent_core.agents.media_prepocess_agent import MediaPreprocessAgent

def run_pipeline(media_path: str | Path, task_type: str = 'image'):

    # 日志记录实例
    logger = PipelineLogger()

    # 初始化仓库， JSON版本
    base_path = Path(__file__).parent
    MEDIA_ROOT = base_path / "media"

    safety_json = base_path / 'config' / 'safety_rules.json'
    review_json = base_path / 'config' / 'review_verify_rules.json'
    repo = JsonRuleRepo(safety_json, review_json)

    # 校验输入文件
    media_path = Path(media_path)
    if not media_path.is_absolute():
        # 如果传入的是相对路径，基于MEDIA_ROOT拼接
        media_path = MEDIA_ROOT / media_path

    if not media_path.exists():
        raise FileNotFoundError(f"媒体文件不存在！路径: {media_path.resolve()}")
    logger.info(f"【输入媒体文件】{media_path.resolve()}")

    # 实例化工具注册器
    registry = ToolRegistry(logger)

    # 实例化工具并注册
    registry.register(YoloDetectTool())
    registry.register(RuleRetrievalTool(repo=repo))
    registry.register(LlmVisonAnalyzeTool())
    # 新增：注册视频抽帧工具
    registry.register(VideoFrameExtractTool())

    # 实例化 Agent
    media_pre_agent = MediaPreprocessAgent(registry, logger)
    perception_agent = PerceptionAgent(registry, logger)
    risk_agent = RiskAnalyzeAgent(registry, logger)
    review_agent = ReviewAgent(registry, logger, repo=repo)

    # 创建任务内存对象
    mem = TaskMemory.create_new_task(str(media_path), task_type)
    print("===== 开始执行多Agent工地安全检测 =====")
    output_frame_dir = str(base_path / "output" / "video_frames")
    media_pre_agent.run(mem, output_frame_dir=output_frame_dir)

    all_hazards = []
    all_marked_paths = []

    for frame_path, ts in zip(mem.frame_paths, mem.frame_timestamps):
        print(f"------ 处理帧：视频时间 {ts:.2f}s，帧文件：{frame_path} ------")
        mem.current_frame_path = frame_path
        mem.current_timestamp = ts

        # 动态生成本帧标注图路径，区分图片/视频帧
        mark_dir = base_path / "output" / "mark_image" / mem.task_id
        mark_dir.mkdir(parents=True, exist_ok=True)
        if task_type == "video":
            marked_save_path = str(mark_dir / f"marked_{ts:.2f}s.jpg")
        else:
            marked_save_path = str(mark_dir / "output_mark.jpg")

        # 阶段1：感知Agent
        perception_agent.run(mem, save_mark_path=marked_save_path)
        # 阶段2：风险研判Agent
        risk_agent.run(mem)
        # 阶段3：证据复核Agent
        frame_hazards = review_agent.run(mem)

        all_marked_paths.append(marked_save_path)
        for hazard in frame_hazards:
            hazard.frame_time = ts
        all_hazards.extend(frame_hazards)

        print(f"帧 {ts:.2f}s 复核完成，本帧隐患数量：{len(frame_hazards)}")

        # ========== 输出最终结果 ==========
    print("\n------ 【复核完成，最终研判结果】 ------")
    for hazard in all_hazards:
        print(f"隐患类型: {hazard.danger_type}，等级：{hazard.risk_level}，置信：{hazard.uncertainty}")
        print(f"描述：{hazard.description}")
        print(f"整改建议：{hazard.suggestion}\n")

    # 打印冲突记录
    if hasattr(mem, "conflict_logs") and len(mem.conflict_logs) > 0:
        print("------ 检测到 Agent 意见冲突记录 ------")
        for item in mem.conflict_logs:
            print(item)
    else:
        print("------ 本次检测无Agent意见冲突 ------")

    exporter = PdfExporter()
    pdf_output = Path(__file__).parent / "output" / "report" / f"{mem.task_id}.pdf"

    try:
        if task_type == "video":
            pdf_original_img = mem.frame_paths[0]
        else:
            pdf_original_img = str(media_path)
        exporter.export(
            pdf_save_path=str(pdf_output),
            original_img_path=pdf_original_img,
            marked_img_path=all_marked_paths[0],
            task_mem=mem,
            hazard_list=all_hazards,
            all_marked_paths=all_marked_paths,
            media_type=task_type
        )
    except Exception as e:
        print(f'PDF导出异常：{e}')

    return mem, all_hazards

if __name__ == '__main__':
    base = Path(__file__).parent / "media"
    # ===== 切换测试只需要注释/取消注释 =====
    # 图片
    # media_file = "image/test.jpg"
    # task_type = "image"

    # 视频测试
    media_file = "video/test.mp4"
    task_type = "video"

    full_media_path = base / media_file
    mem, hazards = run_pipeline(full_media_path, task_type)
