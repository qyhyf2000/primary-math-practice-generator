"""测试数据库管理"""
import pytest
from src.question_bank.db_manager import DBManager
from src.question_bank.models import Question


@pytest.fixture
def db():
    database = DBManager(":memory:")
    yield database
    database.close()


class TestDBManager:
    def test_insert_and_query(self, db):
        q = Question(unit=1, section="oral_calc", difficulty=1,
                     content="5+3=", answer="8")
        rowid = db.insert_question(q)
        assert rowid is not None
        assert not db.is_empty()
        total, _ = db.get_question_count()
        assert total == 1

    def test_content_dedup(self, db):
        q1 = Question(unit=1, section="oral_calc", difficulty=1,
                      content="5+3=", answer="8")
        q2 = Question(unit=1, section="oral_calc", difficulty=1,
                      content="5+3=", answer="8")
        db.insert_question(q1)
        db.insert_question(q2)
        total, _ = db.get_question_count()
        assert total == 1

    def test_reset(self, db):
        q = Question(unit=1, section="oral_calc", difficulty=1,
                     content="5+3=", answer="8")
        db.insert_question(q)
        db.reset()
        assert db.is_empty()

    def test_get_questions_by_section(self, db):
        for i in range(3):
            db.insert_question(Question(
                unit=1, section="oral_calc", difficulty=1,
                content=f"{i}+{i}=", answer=f"{i*2}"
            ))
        qs = db.get_questions(section="oral_calc", limit=10)
        assert len(qs) == 3

    def test_get_questions_by_unit(self, db):
        db.insert_question(Question(unit=1, section="oral_calc", difficulty=1,
                                    content="1+1=", answer="2"))
        db.insert_question(Question(unit=2, section="oral_calc", difficulty=1,
                                    content="2+2=", answer="4"))
        qs = db.get_questions(section="oral_calc", unit_filter=[1], limit=10)
        assert len(qs) == 1
        assert qs[0].unit == 1

    def test_record_exam(self, db):
        q = Question(unit=1, section="oral_calc", difficulty=1,
                     content="5+3=", answer="8")
        db.insert_question(q)
        total, _ = db.get_question_count()
        assert total == 1
        # record_exam needs real IDs, get them from query
        qs = db.get_questions(section="oral_calc", limit=1)
        db.record_exam("测试卷", [qs[0].id])
        usage = db.get_usage_summary(weeks=52)
        assert qs[0].id in usage

    def test_get_questions_by_tier(self, db):
        # 插入题目
        q1 = Question(unit=1, section="oral_calc", difficulty=1,
                      content="tier0", answer="0")
        q2 = Question(unit=1, section="oral_calc", difficulty=1,
                      content="tier1", answer="1")
        db.insert_question(q1)
        db.insert_question(q2)

        qs = db.get_questions(section="oral_calc", limit=10)
        # 记录 q2 使用一次，使其进入 tier 1
        db.record_exam("测试卷", [qs[1].id])

        # tier 查询：tier 0 的应该排在前面
        results = db.get_questions_by_tier(section="oral_calc", limit=10)
        assert len(results) == 2
        assert results[0][1] == 0  # 第一题 tier=0
        assert results[1][1] == 1  # 第二题 tier=1

    def test_available_units(self, db):
        db.insert_question(Question(unit=3, section="oral_calc", difficulty=1,
                                    content="3+3=", answer="6"))
        db.insert_question(Question(unit=5, section="oral_calc", difficulty=1,
                                    content="5+5=", answer="10"))
        units = db.get_available_units()
        assert 3 in units
        assert 5 in units

    def test_context_manager(self):
        with DBManager(":memory:") as db:
            assert db.is_empty()
            db.insert_question(Question(unit=1, section="oral_calc", difficulty=1,
                                        content="ctx", answer="test"))
            total, _ = db.get_question_count()
            assert total == 1
