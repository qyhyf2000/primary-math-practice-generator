"""测试算法题目生成器"""
from src.question_bank.question_generator import generate_questions


class TestGenerateQuestions:
    def test_generate_oral_calc(self):
        qs = generate_questions(count=5, sections=["oral_calc"])
        assert len(qs) <= 5
        for q in qs:
            assert q.content
            assert q.answer
            assert q.section == "oral_calc"
            assert 1 <= q.difficulty <= 5

    def test_generate_fill_blank(self):
        qs = generate_questions(count=3, sections=["fill_blank"])
        for q in qs:
            assert q.section == "fill_blank"

    def test_generate_with_units(self):
        qs = generate_questions(count=5, units=[1])
        for q in qs:
            assert q.unit == 1

    def test_generate_content_not_empty(self):
        qs = generate_questions(count=10)
        assert len(qs) >= 1
        for q in qs:
            assert len(q.content) > 0
            assert len(q.answer) > 0
