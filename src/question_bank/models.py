"""题库数据模型"""
from dataclasses import dataclass, field
from typing import Optional, List
import json


@dataclass
class Question:
    """题目数据模型"""
    unit: int               # 年级内单元编号
    section: str
    difficulty: int
    content: str
    answer: str
    grade: int = 2          # 年级 1-6
    term: int = 2           # 学期 1=上册, 2=下册
    id: Optional[int] = None
    options: Optional[str] = None
    knowledge_point: str = ""
    tags: str = ""
    source: str = "seed"
    created_at: str = ""

    def get_options_list(self) -> List[str]:
        """解析选择题选项为列表"""
        if not self.options:
            return []
        try:
            return json.loads(self.options)
        except json.JSONDecodeError:
            return []


@dataclass
class ExamSection:
    """试卷的一个题型"""
    title: str
    score_per_question: int
    section_id: str
    questions: List[Question] = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return len(self.questions) * self.score_per_question


@dataclass
class Exam:
    """完整试卷"""
    title: str
    sections: List[ExamSection] = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return sum(s.total_score for s in self.sections)

    @property
    def total_questions(self) -> int:
        return sum(len(s.questions) for s in self.sections)

    def all_question_ids(self) -> List[int]:
        ids = []
        for s in self.sections:
            for q in s.questions:
                if q.id is not None:
                    ids.append(q.id)
        return ids
