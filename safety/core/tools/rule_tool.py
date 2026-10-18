from safety.core.agent_core.tool_registry import BaseTool
from safety.core.agent_core.datamodels import TaskMemory
from safety.core.agent_core.repository import BaseRuleRepo

class RuleRetrievalTool(BaseTool):
    name = 'rule_retrieval'
    description = '工地安全规则检索工具，根据隐患关键词返回对应的安全规范'

    def __init__(self, repo: BaseRuleRepo):
        # 内置建议安全规则库，后续可以扩充
        # self.rule_db = {
        #     "安全帽": "建筑施工现场作业人员必须佩戴安全帽，未佩戴属于重大安全隐患，风险等级高。",
        #     "脚手架": "脚手架搭设必须稳固，不得缺少防护栏杆，违规属于高风险隐患。",
        #     "临边": "建筑临边区域必须设置防护设施，无防护属于高风险隐患。",
        #     "反光衣": "现场施工人员进入工地应穿戴反光安全背心，未穿戴为中风险隐患。"
        # }
        self.repo = repo

    def run(self, task_memory: TaskMemory, **kwargs) -> dict:
        keywords = kwargs["keywords"]
        rule_text = self.repo.search_safety_rules(keywords)
        return {
            "rules": rule_text,
        }