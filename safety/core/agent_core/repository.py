import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class BaseRuleRepo(ABC):
    """规则仓库抽象基类"""
    @abstractmethod
    def search_safety_rules(self, keywords: List[str]) -> str:
        """根据关键词搜索安全规范文本，返回拼接后的规则字符串"""
        pass

    @abstractmethod
    def load_review_rules(self) -> List[Dict[str, Any]]:
        """加载复核校验规则列表，提供 ReviewAgent 使用"""
        pass


class JsonRuleRepo(BaseRuleRepo):
    """JSON文件实现：用于开发调试"""
    def __init__(self, safety_rule_json_path: Path, review_rule_json_path: Path):
        self.safety_rule_json_path = safety_rule_json_path
        self.review_rule_json_path = review_rule_json_path

        # 预加载安全规则
        with open(self.safety_rule_json_path, "r", encoding="utf-8") as f:
            self.safety_db: Dict[str, str] = json.load(f)
        # 预加载复核规则
        with open(self.review_rule_json_path, "r", encoding="utf-8") as f:
            self.review_rules: List[Dict[str, Any]] = json.load(f)

    def search_safety_rules(self, keywords: List[str]) -> str:
        matched_rules = []
        for kw in keywords:
            for rule_key, rule_text in self.safety_db.items():
                if kw in rule_key or rule_key in kw:
                    matched_rules.append(rule_text)
        if not matched_rules:
            return "无匹配专项安全规范，按通用工地安全要求评估"
        return "\n".join(matched_rules)

    def load_review_rules(self) -> List[Dict[str, Any]]:
        return self.review_rules

class SqliteRuleRepo(BaseRuleRepo):
    """SQLite实现（后续切换用，当前可以先不运行，保留代码）"""
    def __init__(self, db_path: str):
        import sqlite3
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def search_safety_rules(self, keywords: List[str]) -> str:
        """从sqlite安全规则表检索"""
        matched_rules = []
        cursor = self.conn.cursor()
        for kw in keywords:
            rows = cursor.execute(
                "SELECT rule_text FROM safety_rule WHERE rule_key LIKE ?",
                (f"%{kw}%",)
            ).fetchall()
            for row in rows:
                matched_rules.append(row["rule_text"])
        if not matched_rules:
            return "无匹配专项安全规范，按通用工地安全要求评估"
        return "\n".join(matched_rules)

    def load_review_rules(self) -> List[Dict[str, Any]]:
        """加载复核规则，keywords字段是json字符串，需要反序列化"""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM review_verify_rule").fetchall()
        result = []
        for row in rows:
            item = {
                "keywords": json.loads(row["keywords"]),
                "require_yolo_target": row["require_yolo_target"],
                "desc": row["desc"]
            }
            result.append(item)
        return result

    def close(self):
        self.conn.close()