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
# 新增导包
from safety.core.agent_core.pdf_exporter import PdfExporter

def run_pipeline(media_path: str | Path, task_type: str = 'image'):

    # 日志记录实例
    logger = PipelineLogger()

    # 初始化仓库， JSON版本
    base_path = Path(__file__).parent
    safety_json = base_path / 'config' / 'safety_rules.json'
    review_json = base_path / 'config' / 'review_verify_rules.json'
    repo = JsonRuleRepo(safety_json, review_json)

    # 实例化工具注册器
    registry = ToolRegistry(logger)

    # 实例化工具并注册
    registry.register(YoloDetectTool())
    registry.register(RuleRetrievalTool(repo=repo))
    registry.register(LlmVisonAnalyzeTool())



    mem = TaskMemory.create_new_task(media_path, 'image')
    # 1. 运行感知
    p_agent = PerceptionAgent(registry, logger)
    p_agent.run(mem, save_mark_path='./output/mark_image.jpg')

    # 2. 再研判
    a_agent = RiskAnalyzeAgent(registry, logger)
    res = a_agent.run(mem)

    # 3. 再复核
    r_agent = ReviewAgent(registry, logger, repo=repo)
    final_hazards = r_agent.run(mem)

    print('------ 最终研判结果 ------')
    for h in final_hazards:
        print(f'隐患类型: {h.danger_type}， 等级：{h.risk_level} ，描述：: {h.description}')

    if hasattr(mem, "conflict_logs") and len(mem.conflict_logs) > 0:
        print("------ 检测到 Agent 意见冲突记录 ------")
        for c in mem.conflict_logs:
            print(c)

    # ============ 添加 PDF 导出测试代码 =============
    exporter = PdfExporter()
    pdf_output = Path(__file__).parent / "output"  / "output.pdf"

    try:
        exporter.export(
            pdf_save_path=str(pdf_output),
            original_img_path=str(media_path),
            marked_img_path=str('./output/mark_image.jpg'),
            task_mem=mem,
            hazard_list=final_hazards
        )
    except Exception as e:
        print(e)
    # ================================================

if __name__ == '__main__':
    # 图片测试
    media_path = './media/image/test.jpg'
    task_type = 'image'
    run_pipeline(media_path, task_type)