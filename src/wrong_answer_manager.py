"""错题本管理 — 录入错题、生成重练卷"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path


WRONG_SCHEMA = """
CREATE TABLE IF NOT EXISTS wrong_answers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    wrong_answer TEXT DEFAULT '',
    wrong_at    TEXT DEFAULT (datetime('now','localtime')),
    reviewed    INTEGER DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_wrong_question
    ON wrong_answers(question_id);

CREATE INDEX IF NOT EXISTS idx_wrong_date
    ON wrong_answers(wrong_at);
"""


class WrongAnswerManager:
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self.conn.executescript(WRONG_SCHEMA)
        self.conn.commit()

    def record_wrong(self, question_id: int, student_answer: str = "") -> int:
        """记录一道错题"""
        cur = self.conn.execute(
            "INSERT INTO wrong_answers (question_id, wrong_answer) VALUES (?, ?)",
            (question_id, student_answer)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_wrong_question_ids(self, limit: int = 50) -> List[int]:
        """获取错题 ID 列表（未复习的优先，按时间倒序）"""
        rows = self.conn.execute("""
            SELECT DISTINCT question_id FROM wrong_answers
            ORDER BY reviewed ASC, wrong_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [r[0] for r in rows]

    def get_wrong_stats(self) -> dict:
        """获取错题统计"""
        total = self.conn.execute(
            "SELECT COUNT(DISTINCT question_id) FROM wrong_answers"
        ).fetchone()[0]
        unreviewed = self.conn.execute(
            "SELECT COUNT(DISTINCT question_id) FROM wrong_answers WHERE reviewed = 0"
        ).fetchone()[0]
        recent = self.conn.execute("""
            SELECT COUNT(DISTINCT question_id) FROM wrong_answers
            WHERE wrong_at >= datetime('now', 'localtime', '-7 days')
        """).fetchone()[0]
        return {"total": total, "unreviewed": unreviewed, "recent_7d": recent}

    def mark_reviewed(self, question_id: int):
        """标记错题已复习"""
        self.conn.execute(
            "UPDATE wrong_answers SET reviewed = 1 WHERE question_id = ?",
            (question_id,)
        )
        self.conn.commit()

    def get_wrong_detail(self, limit: int = 20) -> List[dict]:
        """获取错题详情（含题目内容）"""
        rows = self.conn.execute("""
            SELECT w.id, w.question_id, w.wrong_answer, w.wrong_at, w.reviewed,
                   q.content, q.answer, q.grade, q.term, q.knowledge_point
            FROM wrong_answers w
            JOIN questions q ON w.question_id = q.id
            ORDER BY w.reviewed ASC, w.wrong_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [{
            "wrong_id": r[0], "question_id": r[1], "wrong_answer": r[2],
            "wrong_at": r[3], "reviewed": r[4], "content": r[5],
            "answer": r[6], "grade": r[7], "term": r[8],
            "knowledge_point": r[9],
        } for r in rows]

    def clear_all(self):
        """清空错题本"""
        self.conn.execute("DELETE FROM wrong_answers")
        self.conn.commit()
