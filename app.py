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

UNIT_NAMES = {
    1: "第一单元 除法",
    2: "第二单元 混合运算",
    3: "第三单元 生活中的大数",
    4: "第四单元 测量",
    5: "第五单元 加与减",
    6: "第六单元 认识图形",
    7: "第七单元 时分秒",
    8: "第八单元 调查与记录",
}

SECTION_NAMES = {
    "oral_calc": "口算题",
    "fill_blank": "填空题",
    "choice": "选择题",
    "vertical_calc": "竖式/脱式计算",
    "word_problem": "解决问题",
}


# ============================================================
# 回调函数
# ============================================================

def on_generate(week: str, units_selected: list) -> tuple:
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

    db = DBManager(config.get_db_path())
    try:
        if db.is_empty():
            db.insert_batch(get_all_seed_questions())

        builder = ExamBuilder(config, db)
        exam = builder.build_exam(week_label=week or "", unit_filter=units)

        renderer = DocxRenderer(config)
        output_name = f"{config.grade_name}{config.grade_term}_周末练习卷"
        if week:
            output_name += f"_第{week}周"
        output_name += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path = os.path.join(config.get_output_dir(), f"{output_name}.docx")
        filepath = renderer.render(exam, output_path)

        lines = [
            exam.title,
            f"总分: {exam.total_score} 分 | 共 {exam.total_questions} 题",
            "",
        ]
        for sec in exam.sections:
            lines.append(
                f"  {sec.title}: {len(sec.questions)}题 / {sec.total_score}分"
            )

        return "\n".join(lines), filepath
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"生成失败: {e}", None
    finally:
        db.close()


def on_refresh_stats() -> tuple:
    """刷新题库统计"""
    db = DBManager(config.get_db_path())
    try:
        if db.is_empty():
            return "题库为空，请先在「生成试卷」页生成一次试卷以导入初始数据", []

        total, by_section = db.get_question_count()
        available_units = db.get_available_units()

        overview = (
            f"**题目总数**: {total} 题\n\n"
            f"**涵盖单元**: {', '.join(str(u) for u in available_units)}\n\n"
            f"**教材**: {config.textbook} {config.grade_name}{config.grade_term}"
        )

        rows = []
        for section_id, name in SECTION_NAMES.items():
            dist = by_section.get(section_id, {})
            subtotal = sum(dist.values())
            row = [name] + [dist.get(i, 0) for i in range(1, 6)] + [subtotal]
            rows.append(row)

        return overview, rows
    finally:
        db.close()


def on_reload_seed() -> str:
    """重置种子数据"""
    db = DBManager(config.get_db_path())
    try:
        db.reset()
        seed_qs = get_all_seed_questions()
        db.insert_batch(seed_qs)
        total, _ = db.get_question_count()
        return f"已重置题库，重新导入 {total} 道种子题目"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"重置失败: {e}"
    finally:
        db.close()


def on_update_bank() -> str:
    """一键更新题库（算法生成 + 网络抓取 + 本地导入）"""
    db = DBManager(config.get_db_path())
    try:
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
    finally:
        db.close()


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
        f"**排重**: {config.get_dedup_window_weeks()} 周窗口"
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
                inputs=[week, units],
                outputs=[preview, file_dl],
            )

        # ===== Tab 2: 题库管理 =====
        with gr.Tab("题库管理"):
            with gr.Row():
                btn_stats = gr.Button("刷新统计", variant="secondary")
                btn_update = gr.Button("更新题库（自动生成+网络抓取）", variant="primary")
                btn_reload = gr.Button("重置导入种子数据", variant="stop")

            stats_text = gr.Markdown("点击「刷新统计」查看题库状态")

            stats_table = gr.Dataframe(
                headers=["题型", "难度1", "难度2", "难度3", "难度4", "难度5", "小计"],
                label="题型 × 难度分布",
                interactive=False,
            )

            msg = gr.Textbox(label="操作结果", interactive=False)

            btn_stats.click(
                fn=on_refresh_stats,
                inputs=[],
                outputs=[stats_text, stats_table],
            )
            btn_update.click(fn=on_update_bank, inputs=[], outputs=[msg])
            btn_reload.click(fn=on_reload_seed, inputs=[], outputs=[msg])

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
