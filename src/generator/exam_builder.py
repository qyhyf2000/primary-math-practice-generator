"""试卷组装器 - 协调选题和排重"""
from typing import List, Optional
from ..config.config_manager import ConfigManager
from ..question_bank.db_manager import DBManager
from ..question_bank.models import Exam, ExamSection
from .question_picker import QuestionPicker, NotEnoughQuestionsError


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
    ) -> Exam:
        """
        构建一份试卷。

        参数：
            week_label: 周次标签
            unit_filter: 限定单元（如 [1,2,5]），None=全范围
            section_filter: 限定题型（如 ["oral_calc", "word_problem"]），None=全部
            tag_filter: 按标签过滤（如 "图形"），跨题型搜索
        """
        dedup_weeks = self.config.get_dedup_window_weeks()
        exclude_ids = self.db.get_recently_used_ids(weeks=dedup_weeks)

        title = self.config.exam_title(week_label)
        exam = Exam(title=title)

        for section_cfg in self.config.get_sections():
            section_id = section_cfg["id"]

            # 题型过滤：跳过不在 filter 中的 section
            if section_filter and section_id not in section_filter:
                continue

            count = section_cfg["count"]
            diff_range = tuple(section_cfg["difficulty_range"])

            try:
                questions = self.picker.pick_for_section(
                    section_id=section_id,
                    count=count,
                    difficulty_range=diff_range,
                    exclude_ids=exclude_ids,
                    unit_filter=unit_filter,
                    tag_filter=tag_filter,
                )
            except NotEnoughQuestionsError:
                questions = self.picker.pick_for_section(
                    section_id=section_id,
                    count=count,
                    difficulty_range=diff_range,
                    exclude_ids=[],
                    unit_filter=unit_filter,
                    tag_filter=tag_filter,
                )

            if questions:
                section = ExamSection(
                    title=section_cfg["title"],
                    score_per_question=section_cfg["score_per_question"],
                    section_id=section_id,
                    questions=questions,
                )
                exam.sections.append(section)

        self.db.record_exam(exam.title, exam.all_question_ids())
        return exam
