"""题目选择器 - 按使用次数分层 + 难度分层随机抽取"""
import random
from typing import List, Optional, Tuple
from ..question_bank.db_manager import DBManager
from ..question_bank.models import Question


class NotEnoughQuestionsError(Exception):
    """题库中可用题目数量不足"""
    pass


class QuestionPicker:
    def __init__(self, db: DBManager):
        self.db = db

    def pick_for_section(
        self,
        section_id: str,
        count: int,
        difficulty_range: Tuple[int, int],
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
        grade: int = 2,
        term: int = 2,
    ) -> List[Question]:
        """按使用次数分层 + 难度分层随机抽取题目。"""
        lo, hi = difficulty_range

        if hi <= lo:
            return self._pick_by_tier(
                section_id, count, lo, hi, unit_filter, tag_filter, grade, term
            )

        mid = (lo + hi) // 2
        low_count = max(1, int(count * 0.4))
        high_count = max(1, int(count * 0.4))
        flex_count = count - low_count - high_count

        results: List[Question] = []
        picked_ids: set = set()

        low_qs = self._pick_by_tier(
            section_id, low_count, lo, mid, unit_filter, tag_filter, grade, term
        )
        self._add_unique(results, low_qs, picked_ids)

        high_qs = self._pick_by_tier(
            section_id, high_count, mid + 1, hi, unit_filter, tag_filter, grade, term
        )
        self._add_unique(results, high_qs, picked_ids)

        flex_qs = self._pick_by_tier(
            section_id, flex_count, lo, hi, unit_filter, tag_filter, grade, term
        )
        self._add_unique(results, flex_qs, picked_ids)

        if len(results) < count:
            remaining = count - len(results)
            more_qs = self._pick_by_tier(
                section_id, remaining, lo, hi, unit_filter, tag_filter, grade, term
            )
            self._add_unique(results, more_qs, picked_ids)

        random.shuffle(results)
        return results[:count]

    def _pick_by_tier(
        self,
        section_id: str,
        count: int,
        difficulty_min: int,
        difficulty_max: int,
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
        grade: int = 2,
        term: int = 2,
    ) -> List[Question]:
        """按使用次数层级从低到高选取题目"""
        candidates = self.db.get_questions_by_tier(
            section=section_id,
            difficulty_min=difficulty_min,
            difficulty_max=difficulty_max,
            limit=max(count * 5, 50),
            unit_filter=unit_filter,
            tag_filter=tag_filter,
            grade=grade,
            term=term,
        )

        # 按 tier 分组
        tiers: dict = {}
        for q, tier in candidates:
            tiers.setdefault(tier, []).append(q)

        results: List[Question] = []
        picked_ids: set = set()

        for tier in sorted(tiers.keys()):
            if len(results) >= count:
                break
            needed = count - len(results)
            pool = [q for q in tiers[tier] if q.id not in picked_ids]
            random.shuffle(pool)
            for q in pool[:needed]:
                results.append(q)
                picked_ids.add(q.id)

        if len(results) < count:
            raise NotEnoughQuestionsError(
                f"{section_id} 在难度 [{difficulty_min},{difficulty_max}] 范围内可用题目不足 "
                f"(需要{count}题, 仅{len(results)}题可用)"
            )

        return results

    @staticmethod
    def _add_unique(results: List[Question], new_qs: List[Question],
                    seen_ids: set):
        for q in new_qs:
            if q.id not in seen_ids:
                results.append(q)
                seen_ids.add(q.id)
