#!/usr/bin/env python3
"""
小学数学练习试卷生成系统 — Gradio Web UI

用法:
    python app.py          # 启动 Web UI
    python main.py ui      # 等效入口
"""
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from src.config.config_manager import ConfigManager
from src.question_bank.db_manager import DBManager
from src.question_bank.seed_data import get_all_seed_questions
from src.question_bank.sync_engine import SyncEngine
from src.generator.exam_builder import ExamBuilder
from src.renderer.docx_renderer import DocxRenderer

config = ConfigManager()

UNIT_NAMES = config.get_units()

SECTION_NAMES = {
    "oral_calc": "口算题",
    "fill_blank": "填空题",
    "choice": "选择题",
    "vertical_calc": "竖式/脱式计算",
    "word_problem": "解决问题",
}


# ============================================================
# 题型映射
TYPE_OPTIONS = [
    "全部题型",
    "口算题",
    "填空题",
    "选择题",
    "竖式/脱式计算",
    "解决问题",
    "图形题",
]

TYPE_TO_SECTION = {
    "口算题": "oral_calc",
    "填空题": "fill_blank",
    "选择题": "choice",
    "竖式/脱式计算": "vertical_calc",
    "解决问题": "word_problem",
    # "图形题" 用 tag 过滤，不走 section filter
}


# 回调函数
# ============================================================

def on_generate(week: str, units_selected: list, section_type: str) -> tuple:
    """生成试卷"""
    # 提取单元编号
    units = []
    for label in (units_selected or []):
        for num, name in UNIT_NAMES.items():
            if name == label:
                units.append(num)
                break

    if not units:
        return "请至少选择一个单元", None

    # 解析题型过滤
    section_filter = None
    tag_filter = None
    if section_type and section_type != "全部题型":
        if section_type == "图形题":
            tag_filter = "图形"
        elif section_type in TYPE_TO_SECTION:
            section_filter = [TYPE_TO_SECTION[section_type]]

    try:
        with DBManager(config.get_db_path()) as db:
            if db.is_empty():
                db.insert_batch(get_all_seed_questions())

            builder = ExamBuilder(config, db)
            exam = builder.build_exam(
                week_label=week or "",
                unit_filter=units,
                section_filter=section_filter,
                tag_filter=tag_filter,
            )

            renderer = DocxRenderer(config)
            type_tag = f"_{section_type}" if section_type != "全部题型" else ""
            output_name = f"{config.grade_name}{config.grade_term}_周末练习卷{type_tag}"
            if week:
                output_name += f"_第{week}周"
            output_name += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            output_path = os.path.join(config.get_output_dir(), f"{output_name}.docx")
            filepath = renderer.render(exam, output_path)

            lines = [
                exam.title,
                f"题型: {section_type or '全部'} | 总分: {exam.total_score} 分 | 共 {exam.total_questions} 题",
                "",
            ]
            for sec in exam.sections:
                lines.append(f"  {sec.title}: {len(sec.questions)}题 / {sec.total_score}分")

            return "\n".join(lines), filepath
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"生成失败: {e}", None


def on_refresh_stats() -> tuple:
    """刷新题库统计，按使用次数（tier）展示"""
    db = DBManager(config.get_db_path())
    try:
        if db.is_empty():
            return "题库为空，请先在「生成试卷」页生成一次试卷以导入初始数据", [], ""

        total, by_section = db.get_question_count()
        available_units = db.get_available_units()

        # 按 tier 统计（全历史使用次数）
        tier_counts = _get_tier_summary(db)

        overview = (
            f"**题目总数**: {total} 题 | **涵盖单元**: {', '.join(str(u) for u in available_units)}\n\n"
            f"**教材**: {config.textbook} {config.grade_name}{config.grade_term}\n\n"
            f"**选题策略**: 按历史使用次数分层，优先选从未用过的题，全部题目循环复用"
        )

        # 题型 x 难度分布表（保留原有格式）
        rows = []
        for section_id, name in SECTION_NAMES.items():
            dist = by_section.get(section_id, {})
            subtotal = sum(dist.values())
            t0 = tier_counts.get(section_id, {}).get(0, 0)
            t1p = subtotal - t0
            row = (
                [name]
                + [dist.get(i, 0) for i in range(1, 6)]
                + [subtotal]
                + [t0, t1p]
            )
            rows.append(row)

        label_info = (
            f"**层级说明**: Tier 0 = 从未使用过的题目（优先抽取），"
            f"Tier 1+ = 使用过 1 次以上的题目（后续循环使用）"
        )

        return overview, rows, label_info
    finally:
        db.close()


def _get_tier_summary(db: DBManager) -> dict:
    """统计每个题型各 tier 的题目数量"""
    rows = db.conn.execute("""
        SELECT q.section,
               (SELECT COUNT(*) FROM exam_history eh WHERE eh.question_id = q.id) AS tier,
               COUNT(*) AS cnt
        FROM questions q
        GROUP BY q.section, tier
        ORDER BY q.section, tier
    """).fetchall()
    result: dict = {}
    for section, tier, cnt in rows:
        if section not in result:
            result[section] = {}
        result[section][tier] = cnt
    return result


def on_reload_seed() -> str:
    """重置种子数据"""
    try:
        with DBManager(config.get_db_path()) as db:
            db.reset()
            seed_qs = get_all_seed_questions()
            db.insert_batch(seed_qs)
            total, _ = db.get_question_count()
            return f"已重置题库，重新导入 {total} 道种子题目"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"重置失败: {e}"


def on_scrape_url(url: str) -> str:
    """从指定 URL 抓取题目"""
    if not url or not url.startswith("http"):
        return "请输入有效的 URL"
    try:
        with DBManager(config.get_db_path()) as db:
            from src.question_bank.scrapers import scrape_urls
            raw = scrape_urls([url])
            added = 0
            for item in raw:
                if not db.content_exists(item["content"]):
                    from src.question_bank.models import Question
                    q = Question(
                        unit=item.get("unit", 0),
                        section=item.get("section", "oral_calc"),
                        difficulty=item.get("difficulty", 1),
                        content=item["content"],
                        answer=item.get("answer", ""),
                        source="scraped",
                    )
                    db.insert_question(q)
                    added += 1
            return f"从 {url[-40:]} 抓取到 {len(raw)} 题，新入库 {added} 题"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"抓取失败: {e}"


def on_update_bank() -> str:
    """一键更新题库（算法生成 + 网络抓取 + 本地导入）"""
    try:
        with DBManager(config.get_db_path()) as db:
            sync_cfg = config.get_sync_config()
            if not sync_cfg.get("enabled", True):
                return "自动更新未启用（config.yaml 中 sync.enabled: false）"

            engine = SyncEngine(db, sync_cfg)
            result = engine.sync_once()

            parts = []
            parts.append(f"算法生成: +{result['generated']}题")
            if result['scraped'] > 0:
                parts.append(f"网络抓取: +{result['scraped']}题")
            if result['imported'] > 0:
                parts.append(f"本地导入: +{result['imported']}题")

            total = result["generated"] + result["scraped"] + result["imported"]

            if result.get("error"):
                return f"更新完成（总+{total}题）: {', '.join(parts)} | ⚠ {result['error']}"
            return f"更新完成（总+{total}题）: {', '.join(parts)}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"更新失败: {e}"


# 保留旧名称兼容
on_sync = on_update_bank


def on_show_config() -> str:
    """显示配置"""
    lines = [
        f"**年级**: {config.grade_name} | **学期**: {config.grade_term}",
        f"**教材**: {config.textbook}",
        "",
        "**试卷结构**:",
    ]
    for sec in config.get_sections():
        dr = sec["difficulty_range"]
        lines.append(
            f"- {sec['title']}: {sec['count']}题 "
            f"(难度{dr[0]}-{dr[1]}) "
            f"每题{sec['score_per_question']}分"
        )
    rendering = config.get_rendering_config()
    lines.append("")
    lines.append(
        f"**排版**: 标题{rendering['fonts']['title']} "
        f"{rendering['title']['font_size_pt']}pt | "
        f"正文{rendering['fonts']['body']} "
        f"{rendering['body']['font_size_pt']}pt"
    )
    lines.append(
        "**选题策略**: 按使用次数分层，优先抽没做过的题，全部题循环复用"
    )

    # 同步状态
    sync_cfg = config.get_sync_config()
    lines.append("")
    lines.append("**题库更新**:")
    if sync_cfg.get("enabled", True):
        gen_count = sync_cfg.get("generator_count", 30)
        lines.append(f"- 算法生成: 每次 +{gen_count} 题")
        scraper = sync_cfg.get("scraper_url", "")
        lines.append(f"- 网络抓取: {'已配置' if scraper else '未配置（仅本地生成）'}")
        interval = sync_cfg.get("interval_hours", 0)
        if interval > 0:
            lines.append(f"- 定时更新: 每 {interval} 小时")
        else:
            lines.append(f"- 定时更新: 手动触发")
    else:
        lines.append("- 自动更新已禁用")
    lines.append(
        "- 本地导入: 将 .json/.yaml 放入 `data/import/` 自动导入"
    )

    return "\n".join(lines)


# ============================================================
# UI 构建
# ============================================================

def build_ui():
    with gr.Blocks(title="小学数学练习试卷生成系统") as demo:

        gr.Markdown(
            "# 小学数学练习试卷生成系统\n"
            f"**{config.textbook} {config.grade_name}数学{config.grade_term}** "
            "· 周末练习题 · 约20分钟"
        )

        # ===== Tab 1: 生成试卷 =====
        with gr.Tab("生成试卷"):
            with gr.Row():
                with gr.Column(scale=1):
                    section_type = gr.Dropdown(
                        choices=TYPE_OPTIONS,
                        value="全部题型",
                        label="题型筛选",
                    )
                    week = gr.Textbox(
                        label="周次",
                        placeholder="例如: 12（可选）",
                    )
                    units = gr.CheckboxGroup(
                        choices=list(UNIT_NAMES.values()),
                        value=list(UNIT_NAMES.values()),
                        label="限定单元（默认全选）",
                    )
                    btn_gen = gr.Button("生成试卷", variant="primary")

                with gr.Column(scale=2):
                    preview = gr.Textbox(
                        label="试卷信息",
                        lines=12,
                        interactive=False,
                    )
                    file_dl = gr.File(label="下载 Word 试卷")

            btn_gen.click(
                fn=on_generate,
                inputs=[week, units, section_type],
                outputs=[preview, file_dl],
            )

        # ===== Tab 2: 题库管理 =====
        with gr.Tab("题库管理"):
            with gr.Row():
                btn_stats = gr.Button("刷新统计", variant="secondary")
                btn_update = gr.Button("更新题库（算法生成+网络抓取+本地导入）",
                                       variant="primary")
                btn_reload = gr.Button("重置种子数据", variant="stop")

            stats_text = gr.Markdown("点击「刷新统计」查看题库状态")

            stats_table = gr.Dataframe(
                headers=[
                    "题型", "难度1", "难度2", "难度3", "难度4", "难度5",
                    "总题数", "Tier 0 (从未使用)", "Tier 1+ (已使用)",
                ],
                label="题型 x 难度分布（含使用层级）",
                interactive=False,
            )

            usage_label = gr.Markdown("")

            msg = gr.Textbox(label="操作结果", interactive=False)

            btn_stats.click(
                fn=on_refresh_stats,
                inputs=[],
                outputs=[stats_text, stats_table, usage_label],
            )
            btn_update.click(fn=on_update_bank, inputs=[], outputs=[msg])
            btn_reload.click(fn=on_reload_seed, inputs=[], outputs=[msg])

            # 单独抓取 URL
            gr.Markdown("---\n**从指定网页抓取题目**")
            with gr.Row():
                scrape_url_input = gr.Textbox(
                    label="网页 URL",
                    placeholder="粘贴 51test.net 或其他教育网站的题目页面 URL",
                    scale=3,
                )
                btn_scrape = gr.Button("抓取", variant="secondary", scale=1)
            scrape_msg = gr.Textbox(label="抓取结果", interactive=False)
            btn_scrape.click(
                fn=on_scrape_url,
                inputs=[scrape_url_input],
                outputs=[scrape_msg],
            )

        # ===== Tab 3: 系统设置 =====
        with gr.Tab("系统设置"):
            gr.Markdown(on_show_config())
            gr.Markdown(
                "---\n"
                "修改年级、题型、排版参数请编辑 `config.yaml` 文件后重启程序。\n\n"
                "相关文件:\n"
                "- `config.yaml` — 配置文件\n"
                "- `data/question_bank.db` — 题库数据库\n"
                "- `src/question_bank/seed_data.py` — 种子数据\n"
                "- `output/` — 试卷输出目录"
            )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        inbrowser=True,
        show_error=True,
        theme=gr.themes.Soft(),
    )
