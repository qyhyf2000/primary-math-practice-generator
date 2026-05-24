"""SQLite 题库数据库管理"""
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple
from .models import Question


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit            INTEGER NOT NULL CHECK(unit BETWEEN 1 AND 12),
    section         TEXT NOT NULL,
    difficulty      INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 5),
    content         TEXT NOT NULL,
    answer          TEXT NOT NULL,
    options         TEXT,
    knowledge_point TEXT DEFAULT '',
    tags            TEXT DEFAULT '',
    source          TEXT DEFAULT 'seed',
    content_hash    TEXT NOT NULL UNIQUE,
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_section_diff
    ON questions(section, difficulty, unit);

CREATE INDEX IF NOT EXISTS idx_unit
    ON questions(unit);

CREATE TABLE IF NOT EXISTS exam_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    exam_title  TEXT NOT NULL,
    used_at     TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_exam_history_question
    ON exam_history(question_id);

CREATE INDEX IF NOT EXISTS idx_exam_history_date
    ON exam_history(used_at);
"""


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(DB_SCHEMA)
        self.conn.commit()

    @staticmethod
    def _hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    # ---- 增 ----

    def insert_question(self, q: Question) -> int:
        q.content_hash = self._hash_content(q.content)
        cur = self.conn.execute("""
            INSERT OR IGNORE INTO questions
                (unit, section, difficulty, content, answer, options,
                 knowledge_point, tags, source, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (q.unit, q.section, q.difficulty, q.content, q.answer,
              q.options, q.knowledge_point, q.tags, q.source, q.content_hash))
        self.conn.commit()
        return cur.lastrowid

    def insert_batch(self, questions: List[Question]) -> int:
        count = 0
        data = []
        for q in questions:
            h = self._hash_content(q.content)
            data.append((q.unit, q.section, q.difficulty, q.content, q.answer,
                         q.options, q.knowledge_point, q.tags, q.source, h))
        cur = self.conn.executemany("""
            INSERT OR IGNORE INTO questions
                (unit, section, difficulty, content, answer, options,
                 knowledge_point, tags, source, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()
        return cur.rowcount

    # ---- 查 ----

    def get_questions(
        self,
        section: str,
        difficulty_min: int = 1,
        difficulty_max: int = 5,
        limit: int = 100,
        exclude_ids: Optional[List[int]] = None,
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
    ) -> List[Question]:
        sql = """
            SELECT id, unit, section, difficulty, content, answer, options,
                   knowledge_point, tags, source, created_at
            FROM questions
            WHERE section = ?
              AND difficulty BETWEEN ? AND ?
        """
        params = [section, difficulty_min, difficulty_max]

        if exclude_ids:
            placeholders = ",".join("?" * len(exclude_ids))
            sql += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)

        if unit_filter:
            placeholders = ",".join("?" * len(unit_filter))
            sql += f" AND unit IN ({placeholders})"
            params.extend(unit_filter)

        if tag_filter:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag_filter}%")

        sql += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_question(r) for r in rows]

    def _row_to_question(self, row) -> Question:
        return Question(
            id=row[0], unit=row[1], section=row[2], difficulty=row[3],
            content=row[4], answer=row[5], options=row[6],
            knowledge_point=row[7], tags=row[8], source=row[9],
            created_at=row[10],
        )

    def get_question_count(self) -> Tuple[int, dict]:
        total = self.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        by_section = {}
        rows = self.conn.execute(
            "SELECT section, difficulty, COUNT(*) FROM questions GROUP BY section, difficulty ORDER BY section, difficulty"
        ).fetchall()
        for section, diff, cnt in rows:
            if section not in by_section:
                by_section[section] = {}
            by_section[section][diff] = cnt
        return total, by_section

    def get_available_units(self) -> List[int]:
        rows = self.conn.execute(
            "SELECT DISTINCT unit FROM questions ORDER BY unit"
        ).fetchall()
        return [r[0] for r in rows]

    def content_exists(self, content: str) -> bool:
        h = self._hash_content(content)
        row = self.conn.execute(
            "SELECT 1 FROM questions WHERE content_hash = ?", (h,)
        ).fetchone()
        return row is not None

    # ---- 分层查询（按使用次数 tier） ----

    def get_questions_by_tier(
        self,
        section: str,
        difficulty_min: int = 1,
        difficulty_max: int = 5,
        limit: int = 100,
        unit_filter: Optional[List[int]] = None,
        tag_filter: Optional[str] = None,
    ) -> List[Tuple[Question, int]]:
        """返回 (题目, 使用次数)，按使用次数（tier）升序排列。
        tier=0 表示从未被使用过，优先级最高。
        """
        sql = """
            SELECT q.id, q.unit, q.section, q.difficulty, q.content, q.answer,
                   q.options, q.knowledge_point, q.tags, q.source, q.created_at,
                   COALESCE(eh.use_count, 0) AS tier
            FROM questions q
            LEFT JOIN (
                SELECT question_id, COUNT(*) AS use_count
                FROM exam_history
                GROUP BY question_id
            ) eh ON q.id = eh.question_id
            WHERE q.section = ? AND q.difficulty BETWEEN ? AND ?
        """
        params: list = [section, difficulty_min, difficulty_max]

        if unit_filter:
            placeholders = ",".join("?" * len(unit_filter))
            sql += f" AND q.unit IN ({placeholders})"
            params.extend(unit_filter)

        if tag_filter:
            sql += " AND q.tags LIKE ?"
            params.append(f"%{tag_filter}%")

        sql += " ORDER BY tier ASC, RANDOM() LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [(self._row_to_question(r), r[-1]) for r in rows]

    # ---- 排重历史 ----

    def get_recently_used_ids(self, weeks: int = 4) -> List[int]:
        rows = self.conn.execute("""
            SELECT DISTINCT question_id FROM exam_history
            WHERE used_at >= datetime('now', 'localtime', ?)
        """, (f"-{weeks * 7} days",)).fetchall()
        return [r[0] for r in rows]

    def record_exam(self, exam_title: str, question_ids: List[int]):
        data = [(qid, exam_title) for qid in question_ids if qid]
        self.conn.executemany(
            "INSERT INTO exam_history (question_id, exam_title) VALUES (?, ?)",
            data
        )
        self.conn.commit()

    def get_usage_summary(self, weeks: int = 4) -> dict:
        """获取最近N周内的题目使用统计"""
        rows = self.conn.execute("""
            SELECT question_id, COUNT(*) as use_count, MAX(used_at) as last_used
            FROM exam_history
            WHERE used_at >= datetime('now', 'localtime', ?)
            GROUP BY question_id
        """, (f"-{weeks * 7} days",)).fetchall()
        return {
            row[0]: {"use_count": row[1], "last_used": row[2]}
            for row in rows
        }

    def get_available_counts(self, weeks: int = 4) -> dict:
        """按题型统计可用/已用/总数"""
        used_ids = [str(x) for x in self.get_recently_used_ids(weeks)]
        rows = self.conn.execute(
            "SELECT section, COUNT(*) FROM questions GROUP BY section"
        ).fetchall()

        result = {}
        for section, total in rows:
            if used_ids:
                placeholders = ",".join("?" for _ in used_ids)
                used = self.conn.execute(
                    f"SELECT COUNT(*) FROM questions WHERE section = ? AND id IN ({placeholders})",
                    [section] + used_ids
                ).fetchone()[0]
            else:
                used = 0
            result[section] = {"total": total, "used": used, "available": total - used}
        return result

    def is_empty(self) -> bool:
        row = self.conn.execute("SELECT COUNT(*) FROM questions").fetchone()
        return row[0] == 0

    # ---- 管理 ----

    def reset(self):
        # 先删子表（有外键），再删主表
        self.conn.execute("DELETE FROM exam_history")
        self.conn.execute("DELETE FROM questions")
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass
