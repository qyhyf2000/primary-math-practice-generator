"""试卷组装器 - 协调选题和排重"""
import logging
from typing import List, Optional
from ..config.config_manager import ConfigManager
from ..question_bank.db_manager import DBManager
from ..question_bank.models import Exam, ExamSection
from .question_picker import QuestionPicker

logger = logging.getLogger(__name__)


class ExamBuilder:
    def __init__(self, config: ConfigManager, db: DBManager):
        self.config = config
        self.db = db
        self.picker = QuestionPicker(db)

    def build_exam(
        self,
        week_label: str = "",
        unit_filter: Optional[List[int]] = None,
        section_filter: Optional[List[str]] = None,
        tag_filter: Optional[str] = None,
        grade: int = 2,
        term: int = 2,
    ) -> Exam:
        """
        构建一份试卷。选题采用使用次数分层机制。

        参数：
            week_label: 周次标签
            unit_filter: 限定单元
            section_filter: 限定题型
            tag_filter: 按标签过滤
            grade: 年级 1-6
            term: 学期 1=上, 2=下
        """
        # 检查当前年级/学期题目是否足够，不足则按题型分别自动生成
        grade_count = self.db.conn.execute(
            "SELECT COUNT(*) FROM questions WHERE grade=? AND term=?",
            (grade, term)
        ).fetchone()[0]
        if grade_count < 30:
            from ..question_bank.question_generator import generate_questions as gen_qs
            for sec in ["oral_calc", "fill_blank", "choice", "vertical_calc", "word_problem"]:
                new_qs = gen_qs(count=40, sections=[sec], grade=grade, term=term)
                if new_qs:
                    self.db.insert_batch(new_qs)
            logger.info(f"自动生成补充 G{grade}T{term} 题库（原{grade_count}题）")

        title = self.config.exam_title(week_label)
        exam = Exam(title=title)

        for section_cfg in self.config.get_sections():
            section_id = section_cfg["id"]

            if section_filter and section_id not in section_filter:
                continue

            count = section_cfg["count"]
            diff_range = tuple(section_cfg["difficulty_range"])

            try:
                questions = self.picker.pick_for_section(
                    section_id=section_id,
                    count=count,
                    difficulty_range=diff_range,
                    unit_filter=unit_filter,
                    tag_filter=tag_filter,
                    grade=grade,
                    term=term,
                )
            except Exception:
                logger.warning(
                    f"{section_id}: 选取题目失败，跳过此题型"
                )
                continue

            if questions:
                # 严格验证：所有题目必须属于当前年级/学期
                for q in questions:
                    if q.grade != grade or q.term != term:
                        logger.error(
                            f"年级不匹配: 期望G{grade}T{term}, "
                            f"实际G{q.grade}T{q.term}, 题目{q.content[:30]}"
                        )
                questions = [q for q in questions if q.grade == grade and q.term == term]

                section = ExamSection(
                    title=section_cfg["title"],
                    score_per_question=section_cfg["score_per_question"],
                    section_id=section_id,
                    questions=questions,
                )
                exam.sections.append(section)

        self.db.record_exam(exam.title, exam.all_question_ids())
        return exam
