"""
模块: services.question_service.adapters
职责: 提供题目生成适配器（本地/远程）与质量校验。
输入: 概念、难度与生成参数。
输出: 题目结构字典或 None（质量不达标）。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import random
import requests

from common.config.settings import settings


BLOOM_LEVELS = {
    1: "remember",
    2: "understand",
    3: "apply",
    4: "analyze",
    5: "evaluate_or_create",
}


def map_difficulty_to_bloom(difficulty: int) -> str:
    """将难度映射到 Bloom 认知层级。
    输入: difficulty 1-5。
    输出: Bloom 层级字符串。
    作用: 指导题型与校验强度。
    """
    return BLOOM_LEVELS.get(max(1, min(5, difficulty)), "remember")


class QuestionAdapter(ABC):
    """题目生成适配器抽象基类。"""

    @abstractmethod
    def generate(self, concept: str, difficulty: int) -> Dict[str, Any] | None:  # noqa: D401
        """根据概念与难度生成题目。"""
        raise NotImplementedError


def _unique_options(options: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for o in options:
        if o not in seen and o:
            seen.add(o)
            result.append(o)
    return result


def _build_item_by_bloom(concept: str, difficulty: int) -> Dict[str, Any]:
    bloom = map_difficulty_to_bloom(difficulty)
    if bloom in ("remember", "understand"):
        # 单选/判断
        if random.random() < 0.5:
            options = _unique_options([f"与{concept}最相关的定义", f"与{concept}无关的描述", "泛化说法", "无关项"])
            return {
                "concept": concept,
                "difficulty": difficulty,
                "bloomLevel": bloom,
                "type": "single_choice",
                "stem": f"下列关于 {concept} 的说法，哪项最准确？",
                "options": options,
                "answer": options[0],
                "explanation": f"考察对 {concept} 的基本识记与理解。",
            }
        else:
            return {
                "concept": concept,
                "difficulty": difficulty,
                "bloomLevel": bloom,
                "type": "true_false",
                "stem": f"{concept} 与其核心定义一致：'xxx'。此说法是否正确？",
                "answer": True,
                "explanation": f"考察对 {concept} 的判断。",
            }
    elif bloom == "apply":
        # 多选/填空
        options = _unique_options([f"将{concept}用于情境A", f"将{concept}用于情境B", "无关应用", "反例"])
        return {
            "concept": concept,
            "difficulty": difficulty,
            "bloomLevel": bloom,
            "type": "multiple_choice",
            "stem": f"关于 {concept} 的应用，选择所有正确项。",
            "options": options,
            "answers": options[:2],
            "explanation": f"考察对 {concept} 的迁移应用。",
        }
    else:
        # 分析/评价/创造：简答/填空
        if random.random() < 0.5:
            return {
                "concept": concept,
                "difficulty": difficulty,
                "bloomLevel": bloom,
                "type": "short_answer",
                "stem": f"请比较 {concept} 与相近概念的异同，并给出例证。",
                "referenceAnswer": f"围绕 {concept} 的核心维度进行分析。",
            }
        else:
            return {
                "concept": concept,
                "difficulty": difficulty,
                "bloomLevel": bloom,
                "type": "fill_blank",
                "stem": f"{concept} 的关键公式为：____。",
                "blanks": 1,
                "referenceAnswer": "示例答案",
            }


class LocalAdapter(QuestionAdapter):
    """本地占位适配器：依据 Bloom 生成多题型样例。"""

    def generate(self, concept: str, difficulty: int) -> Dict[str, Any] | None:
        item = _build_item_by_bloom(concept, difficulty)
        return item if quality_check(item) else None


class RemoteAdapter(QuestionAdapter):
    """远程 HTTP 适配器：调用外部推理服务。"""

    def generate(self, concept: str, difficulty: int) -> Dict[str, Any] | None:
        try:
            resp = requests.post(
                settings.qgRemoteUrl,
                json={"concept": concept, "difficulty": difficulty, "max_tokens": settings.qgMaxTokens},
                timeout=5,
            )
            resp.raise_for_status()
            item = resp.json()
            # 若远端未给出 bloomLevel，可按难度回填
            item.setdefault("bloomLevel", map_difficulty_to_bloom(difficulty))
            return item if quality_check(item) else None
        except Exception:
            return None


def get_adapter() -> QuestionAdapter:
    """根据配置返回适配器实例。"""
    if settings.qgAdapterType == "remote":
        return RemoteAdapter()
    return LocalAdapter()


def quality_check(item: Dict[str, Any]) -> bool:
    """质量校验：类型通用检查 + 题型特定规则 + 简单评分。
    输入: 题目字典。
    输出: 合格布尔值。
    作用: 拒绝字段缺失、逻辑不一致或内容过短的题目。
    """
    if not item.get("stem") or len(item["stem"]) < 6:
        return False

    qtype = item.get("type")
    if qtype == "single_choice":
        options = item.get("options", [])
        answer = item.get("answer")
        if not isinstance(options, list) or len(options) < 3:
            return False
        if len(set(options)) != len(options):
            return False
        if answer not in options:
            return False
    elif qtype == "multiple_choice":
        options = item.get("options", [])
        answers = item.get("answers", [])
        if not options or not answers:
            return False
        if not set(answers).issubset(set(options)):
            return False
        if len(answers) < 2:
            return False
    elif qtype == "true_false":
        if not isinstance(item.get("answer"), bool):
            return False
    elif qtype == "fill_blank":
        if item.get("blanks", 0) < 1:
            return False
    elif qtype == "short_answer":
        if len(item.get("referenceAnswer", "")) < 6:
            return False
    else:
        return False

    # 简单评分：题干长度与难度系数
    score = min(len(item.get("stem", "")) / 30.0, 1.0) * (0.6 + 0.1 * int(item.get("difficulty", 1)))
    return score >= settings.qgQualityMinScore
