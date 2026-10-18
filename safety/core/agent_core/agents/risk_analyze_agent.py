from safety.core.agent_core.agents.perception_agent import PerceptionAgent
from safety.core.agent_core.datamodels import TaskMemory, RiskAnalyzeResult, SingleHazard
from safety.core.agent_core.tool_registry import ToolRegistry
from safety.core.agent_core.logger import PipelineLogger

class RiskAnalyzeAgent:
    """风险研判智能体：结合YOLO感知证据 + 安全规则 + 图片，调用大模型识别安全隐患"""
    name = 'RiskAnalyzeAgent'

    def __init__(self, tool_registry: ToolRegistry, logger: PipelineLogger):
        self.logger = logger
        self.tool_registry = tool_registry

    def run(self, task_memory: TaskMemory) -> RiskAnalyzeResult:
        self.logger.info(f'[研判 Agent] 开始执行：task_id: {task_memory.task_id}')
        # 取出上一轮感知结果
        perception_result = task_memory.perception_history[-1]
        yolo_raw = perception_result.raw_text

        # 1. 调用规则检索工具
        rule_res = self.tool_registry.call(
            tool_name='rule_retrieval',
            agent_name=self.name,
            task_memory=task_memory,
            keywords=['安全帽', '脚手架', '临边', '反光衣']
        )
        rule_text = rule_res['rules']

        prompt_template = """
你是工地安全研判专家。
已知YOLO检测结果：{yolo_result}
参考安全规范：{rule_text}
请结合图片内容、检测目标、建筑施工安全规范，识别现场安全隐患。

输出要求：
1. 仅输出标准JSON字符串，**禁止```markdown代码块，禁止任何额外说明文字**
2. risk_level 只能取值：高 / 中 / 低
3. 字段说明：
danger_type：简短隐患名称（对应隐患类型）
description：隐患详细描述
risk_level：风险等级（高/中/低）
evidence：图片中的证据依据
suggestion：整改建议
uncertainty：识别置信描述（高置信/一般/低置信）

JSON结构固定如下：
{{
    "risk_list": [
        {{
            "danger_type": "隐患名称",
            "description": "隐患详细描述",
            "risk_level": "高/中/低",
            "evidence": "图片证据描述",
            "suggestion": "整改建议",
            "uncertainty": "高置信/一般/低置信"
        }}
    ]
}}
如果没有发现任何隐患，risk_list为空数组[]
"""
        # 填充YOLO结果+检索到的安全规则到prompt
        prompt = prompt_template.format(yolo_result=yolo_raw, rule_text=rule_text)

        # 3. 调用多模态大模型
        llm_res = self.tool_registry.call(
            tool_name='llm_vision_analyze',
            agent_name=self.name,
            task_memory=task_memory,
            image_path=perception_result.image_path,
            prompt=prompt,
        )
        # 直接读取risk_list，增加异常判断
        if "error" in llm_res:
            self.logger.info(f"[研判 Agent] 视觉大模型调用异常：{llm_res['error']}")
            hazard_list_raw = []
        else:
            hazard_list_raw = llm_res["risk_list"]

        hazard_list = []
        for h in hazard_list_raw:
            hazard = SingleHazard(
                danger_type=h['danger_type'],
                description=h['description'],
                risk_level=h['risk_level'],
                evidence=h['evidence'],
                suggestion=h['suggestion'],
                uncertainty=h['uncertainty']
            )
            hazard_list.append(hazard)
        has_danger = len(hazard_list) > 0
        analysis_result = RiskAnalyzeResult(
            hazard_list=hazard_list,
            has_danger=has_danger,
            uncertainty_global="",
            tool_records=task_memory.all_tool_logs[-2:]
        )
        task_memory.analyze_history.append(analysis_result)
        self.logger.info(f'[研判 Agent] 研判 Agent 完成，识别隐患数量：{len(hazard_list)}')
        return analysis_result