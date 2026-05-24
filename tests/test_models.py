"""测试数据模型"""
import json
from src.question_bank.models import Question, Exam, ExamSection


class TestQuestion:
    def test_creation_defaults(self):
        q = Question(unit=1, section="oral_calc", difficulty=2,
                     content="3+5=", answer="8")
        assert q.unit == 1
        assert q.section == "oral_calc"
        assert q.difficulty == 2
        assert q.content == "3+5="
        assert q.answer == "8"
        assert q.source == "seed"
        assert q.knowledge_point == ""
        assert q.tags == ""
        assert q.id is None

    def test_options_parsing(self):
        q = Question(unit=1, section="choice", difficulty=2,
                     content="test", answer="A",
                     options='["A. 1", "B. 2", "C. 3", "D. 4"]')
        opts = q.get_options_list()
        assert len(opts) == 4
        assert opts[0] == "A. 1"

    def test_options_empty(self):
        q = Question(unit=1, section="oral_calc", difficulty=1,
                     content="test", answer="8")
        assert q.get_options_list() == []

    def test_options_invalid_json(self):
        q = Question(unit=1, section="choice", difficulty=1,
                     content="test", answer="A", options="not-json")
        assert q.get_options_list() == []


class TestExamSection:
    def test_total_score(self):
        qs = [Question(unit=1, section="oral_calc", difficulty=1, content=f"{i}", answer=f"{i}")
              for i in range(5)]
        section = ExamSection(title="口算", score_per_question=2,
                              section_id="oral_calc", questions=qs)
        assert section.total_score == 10
        assert len(section.questions) == 5


class TestExam:
    def test_total_score_and_questions(self):
        qs1 = [Question(unit=1, section="oral_calc", difficulty=1, content=f"{i}", answer=f"{i}")
               for i in range(3)]
        qs2 = [Question(unit=2, section="fill_blank", difficulty=2, content=f"q{i}", answer=f"a{i}")
               for i in range(2)]
        exam = Exam(title="测试卷")
        exam.sections.append(ExamSection(title="口算", score_per_question=1,
                                         section_id="oral_calc", questions=qs1))
        exam.sections.append(ExamSection(title="填空", score_per_question=2,
                                         section_id="fill_blank", questions=qs2))
        assert exam.total_score == 7
        assert exam.total_questions == 5

    def test_all_question_ids(self):
        qs = [Question(unit=1, section="oral_calc", difficulty=1, content=f"{i}", answer=f"{i}")
              for i in range(2)]
        exam = Exam(title="测试卷")
        exam.sections.append(ExamSection(title="口算", score_per_question=1,
                                         section_id="oral_calc", questions=qs))
        ids = exam.all_question_ids()
        # all_question_ids 过滤掉了 None 值（未入库的题目没有 id）
        assert ids == []
