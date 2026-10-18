""""""
from agent_core.tool_registry import BaseTool
from agent_core.datamodels import TaskMemory

class RuleRetrievalTool(BaseTool):
    name = 'rule_retrieval'
    description = '工地安全规则检索工具，根据隐患关键词返回对应的安全规范'

    def __init__(self):
        # 内置建议安全规则库，后续可以扩充
        self.rule_db = {
            "安全帽": "建筑施工现场作业人员必须佩戴安全帽，未佩戴属于重大安全隐患，风险等级高。",
            "脚手架": "脚手架搭设必须稳固，不得缺少防护栏杆，违规属于高风险隐患。",
            "临边": "建筑临边区域必须设置防护设施，无防护属于高风险隐患。",
            "反光衣": "现场施工人员进入工地应穿戴反光安全背心，未穿戴为中风险隐患。"
        }

    def run(self, task_memory: TaskMemory, **kwargs) -> dict:
        keywords = kwargs["keywords"]
        matched_rules = []
        for kw in keywords:
            for rule_key, rule_text in self.rule_db.items():
                if kw in rule_key or rule_key in kw:
                    matched_rules.append(rule_text)
        if not matched_rules:
            matched_rules = ['无匹配专项安全规范，按通用工地安全要求评估']
        return {
            "rules": "\n".join(matched_rules)
        }