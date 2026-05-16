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
    ) -> Exam:
        """
        构建一份完整试卷。

        参数：
            week_label: 周次标签（用于标题和排重记录）
            unit_filter: 限定单元列表（如 [1,2,5]），None=全范围
        """
        # 获取排重列表
        dedup_weeks = self.config.get_dedup_window_weeks()
        exclude_ids = self.db.get_recently_used_ids(weeks=dedup_weeks)

        title = self.config.exam_title(week_label)
        exam = Exam(title=title)

        for section_cfg in self.config.get_sections():
            section_id = section_cfg["id"]
            count = section_cfg["count"]
            diff_range = tuple(section_cfg["difficulty_range"])

            try:
                questions = self.picker.pick_for_section(
                    section_id=section_id,
                    count=count,
                    difficulty_range=diff_range,
                    exclude_ids=exclude_ids,
                    unit_filter=unit_filter,
                )
            except NotEnoughQuestionsError as e:
                # 混入已用过的题目放宽限制
                questions = self.picker.pick_for_section(
                    section_id=section_id,
                    count=count,
                    difficulty_range=diff_range,
                    exclude_ids=[],
                    unit_filter=unit_filter,
                )

            section = ExamSection(
                title=section_cfg["title"],
                score_per_question=section_cfg["score_per_question"],
                section_id=section_id,
                questions=questions,
            )
            exam.sections.append(section)

        # 记录本次使用的题目
        self.db.record_exam(exam.title, exam.all_question_ids())

        return exam
