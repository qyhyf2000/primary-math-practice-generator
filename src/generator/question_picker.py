"""题目选择器 - 按难度分层随机抽取"""
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
        exclude_ids: Optional[List[int]] = None,
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
    ) -> List[Question]:
        """
        从指定题型中按难度分层随机抽取题目。
        tag_filter: 按标签过滤（如 "图形"）
        """
        exclude_ids = exclude_ids or []
        lo, hi = difficulty_range

        if hi <= lo:
            qs = self.db.get_questions(
                section=section_id,
                difficulty_min=lo, difficulty_max=hi,
                limit=count + len(exclude_ids),
                exclude_ids=exclude_ids,
                unit_filter=unit_filter,
                tag_filter=tag_filter,
            )
            if len(qs) < count:
                raise NotEnoughQuestionsError(
                    f"{section_id} 在难度 [{lo},{hi}] 范围内可用题目不足 "
                    f"(需要{count}题, 仅{len(qs)}题可用)"
                )
            random.shuffle(qs)
            return qs[:count]

        mid = (lo + hi) // 2
        low_count = max(1, int(count * 0.4))
        high_count = max(1, int(count * 0.4))
        flex_count = count - low_count - high_count

        picked_ids = set()
        results = []

        low_qs = self._pick_from_range(
            section_id, (lo, mid), low_count, exclude_ids, unit_filter, tag_filter
        )
        self._add_unique(results, low_qs, picked_ids)

        high_qs = self._pick_from_range(
            section_id, (mid + 1, hi), high_count, exclude_ids, unit_filter, tag_filter
        )
        self._add_unique(results, high_qs, picked_ids)

        flex_qs = self._pick_from_range(
            section_id, (lo, hi), flex_count,
            exclude_ids + [q.id for q in results if q.id], unit_filter, tag_filter
        )
        self._add_unique(results, flex_qs, picked_ids)

        if len(results) < count:
            remaining = count - len(results)
            all_exclude = exclude_ids + [q.id for q in results if q.id]
            more_qs = self._pick_from_range(
                section_id, (lo, hi), remaining, all_exclude, unit_filter, tag_filter
            )
            self._add_unique(results, more_qs, picked_ids)

        random.shuffle(results)
        return results[:count]

    def _pick_from_range(
        self, section: str, diff_range: Tuple[int, int],
        limit: int, exclude_ids: List[int],
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
    ) -> List[Question]:
        lo, hi = diff_range
        return self.db.get_questions(
            section=section,
            difficulty_min=lo, difficulty_max=hi,
            limit=max(limit, 1) + len(exclude_ids),
            exclude_ids=exclude_ids,
            unit_filter=unit_filter,
            tag_filter=tag_filter,
        )

    @staticmethod
    def _add_unique(results: List[Question], new_qs: List[Question],
                    seen_ids: set):
        for q in new_qs:
            if q.id not in seen_ids:
                results.append(q)
                seen_ids.add(q.id)
