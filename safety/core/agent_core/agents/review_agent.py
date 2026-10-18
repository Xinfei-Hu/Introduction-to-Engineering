from safety.core.agent_core.datamodels import TaskMemory, RiskAnalyzeResult, SingleHazard
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.logger import PipelineLogger
from safety.core.agent_core.repository import BaseRuleRepo

class ReviewAgent:
    """
    证据复核智能体【课题要求第三个Agent】
    输入：感知Agent的检测证据 + 风险分析Agent输出隐患
    职责：校验隐患真实性，处理感知与研判意见不一致，过滤大模型幻觉，修正置信度
    """
    name = "ReviewAgent"

    def __init__(self, tool_registry: ToolRegistry, logger: PipelineLogger, repo: BaseRuleRepo):
        self.registry = tool_registry
        self.logger = logger
        self.hazard_verify_rules = repo.load_review_rules()


    def run(self, task_memory: TaskMemory) -> list[SingleHazard]:
        self.logger.info(f'[证据复核 Agent] 开始执行: task_id {task_memory.task_id} ')
        # 获取上游输出
        perception_result = task_memory.perception_history[-1]
        yolo_raw_text = perception_result.raw_text
        analyze_result: RiskAnalyzeResult = task_memory.analyze_history[-1]
        raw_hazard_list = analyze_result.hazard_list

        person_detected = "person" in yolo_raw_text.lower()
        final_hazard_list = []
        conflict_records =[]

        for hazard in raw_hazard_list:
            # 核心逻辑，数据效验 + 处理意见不一致
            evidence_ok = True
            new_uncertainty = hazard.uncertainty

            matched_rule = None
            for rule in self.hazard_verify_rules:
                if any(k in hazard.danger_type for k in rule['keywords']):
                    matched_rule = rule
                    break

            if matched_rule is None:
                print(f"DEBUG 隐患[{hazard.danger_type}] 未pip任何复核规则，保留，减低置信")
                new_uncertainty = '一般'
            else:
                print(f"DEBUG 隐患[{hazard.danger_type}] 匹配规则: {matched_rule['desc']}")
                required_target = matched_rule['require_yolo_target']
                if required_target == 'person':
                    # 人员类隐患：YOLO必须检测到人，否则冲突
                    if not person_detected:
                        evidence_ok = False
                        conflict_records.append({
                            "hazard_type": hazard.danger_type,
                            "conflict": "风险识别人员隐患, 但YOLO未检测到人员目标"
                        })
                        new_uncertainty = "低置信"

            # 设施隐患：不校验是否有人
            # 设施隐患可后续增加脚手架目标检测校验

            # 证据充足保留，证据不足丢弃

            if evidence_ok:
                hazard.uncertainty = new_uncertainty
                final_hazard_list.append(hazard)
            else:
                self.logger.info(f"[证据复核 Agent] 复核冲突丢弃: {hazard.danger_type}, 缺少感知证据支持")

        task_memory.conflict_logs = conflict_records
        task_memory.review_history = final_hazard_list

        self.logger.info(f"[证据复核 Agent] 完成：原始隐患{len(raw_hazard_list)}条，校验后保留{len(final_hazard_list)}条，冲突{len(conflict_records)}处")
        return final_hazard_list