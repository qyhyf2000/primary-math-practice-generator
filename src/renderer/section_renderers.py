"""各题型渲染函数"""
import json
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from .layout import (
    add_paragraph, set_cjk_font, set_cell_border,
    cell_add_run, set_table_borders,
)
from ..question_bank.models import ExamSection


FONT = "宋体"
HEADING_FONT = "楷体"
BODY_SIZE = 12
HEADING_SIZE = 12


def render_section_heading(doc, section: ExamSection):
    """渲染题型标题，如：一、口算题（每题1分，共10分）"""
    title_text = f"{section.title}（每题{section.score_per_question}分，共{section.total_score}分）"
    add_paragraph(doc, title_text, HEADING_FONT, HEADING_SIZE,
                  bold=True, space_after_pt=4)


def render_oral_calc(doc, section: ExamSection):
    """口算题 — 表格布局，5列×N行"""
    questions = section.questions
    cols = 5
    rows = (len(questions) + cols - 1) // cols

    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, val="single", sz="4")

    for idx, q in enumerate(questions):
        r = idx // cols
        c = idx % cols
        cell = table.cell(r, c)
        cell_add_run(cell, f"{idx + 1}. {q.content}", FONT, BODY_SIZE)

    doc.add_paragraph()


def render_fill_blank(doc, section: ExamSection):
    """填空题 — 段落形式，每题一段"""
    for idx, q in enumerate(section.questions):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"{idx + 1}. {q.content}")
        set_cjk_font(run, FONT, BODY_SIZE)


def render_choice(doc, section: ExamSection):
    """选择题 — 每题一段，选项横向排列"""
    for idx, q in enumerate(section.questions):
        # 题干
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(f"{idx + 1}. {q.content}")
        set_cjk_font(run, FONT, BODY_SIZE)

        # 选项
        options = q.get_options_list()
        if options:
            opt_p = doc.add_paragraph()
            opt_p.paragraph_format.space_after = Pt(4)
            opt_p.paragraph_format.left_indent = Cm(0.8)
            opt_text = "     ".join(options)
            run = opt_p.add_run(opt_text)
            set_cjk_font(run, FONT, BODY_SIZE)


def render_vertical_calc(doc, section: ExamSection):
    """竖式/脱式计算 — 每题后留空白书写区"""
    for idx, q in enumerate(section.questions):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(f"{idx + 1}. {q.content}")
        set_cjk_font(run, FONT, BODY_SIZE)

        # 空白书写区（用空行模拟）
        for _ in range(4):
            blank_p = doc.add_paragraph()
            blank_p.paragraph_format.space_before = Pt(0)
            blank_p.paragraph_format.space_after = Pt(0)
            # 添加一个底边框行作为书写线
            run = blank_p.add_run(" " * 60)
            set_cjk_font(run, FONT, BODY_SIZE)


def render_word_problem(doc, section: ExamSection):
    """解决问题（应用题）— 每题后留列式和答的空白"""
    for idx, q in enumerate(section.questions):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(f"{idx + 1}. {q.content}")
        set_cjk_font(run, FONT, BODY_SIZE)

        # 列式区域
        formula_p = doc.add_paragraph()
        formula_p.paragraph_format.space_before = Pt(8)
        run = formula_p.add_run("列式：")
        set_cjk_font(run, FONT, BODY_SIZE, bold=True)

        for _ in range(3):
            blank_p = doc.add_paragraph()
            blank_p.paragraph_format.space_before = Pt(0)
            blank_p.paragraph_format.space_after = Pt(0)
            run = blank_p.add_run(" " * 60)
            set_cjk_font(run, FONT, BODY_SIZE)

        # 答区域
        answer_p = doc.add_paragraph()
        answer_p.paragraph_format.space_before = Pt(8)
        answer_p.paragraph_format.space_after = Pt(6)
        run = answer_p.add_run("答：")
        set_cjk_font(run, FONT, BODY_SIZE, bold=True)
        run = answer_p.add_run("_" * 50)
        set_cjk_font(run, FONT, BODY_SIZE)


RENDERER_MAP = {
    "oral_calc": render_oral_calc,
    "fill_blank": render_fill_blank,
    "choice": render_choice,
    "vertical_calc": render_vertical_calc,
    "word_problem": render_word_problem,
}
