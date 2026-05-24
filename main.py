#!/usr/bin/env python3
"""
小学数学练习试卷生成系统

用法:
    python main.py generate              # 生成本周试卷
    python main.py generate --week 12    # 指定周次
    python main.py generate --units 1,2  # 限定单元
    python main.py generate --output 自定义名称  # 自定义文件名
    python main.py status                # 查看题库统计
    python main.py seed --reload         # 重置并重新导入种子数据
    python main.py sync                  # 手动触发在线同步
"""
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# 将 src 加入模块搜索路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config.config_manager import ConfigManager
from src.question_bank.db_manager import DBManager
from src.question_bank.seed_data import get_all_seed_questions
from src.question_bank.sync_engine import SyncEngine
from src.generator.exam_builder import ExamBuilder
from src.renderer.docx_renderer import DocxRenderer


TYPE_MAP = {
    "口算题": "oral_calc",
    "填空题": "fill_blank",
    "选择题": "choice",
    "竖式": "vertical_calc",
    "脱式": "vertical_calc",
    "竖式/脱式计算": "vertical_calc",
    "解决问题": "word_problem",
    "应用题": "word_problem",
    "图形题": "图形",
}


def cmd_generate(args, config: ConfigManager):
    """生成一份试卷"""
    with DBManager(config.get_db_path()) as db:
        if db.is_empty() and config.get_seed_on_empty():
            print("题库为空，正在导入内置种子数据...")
            seed_qs = get_all_seed_questions()
            db.insert_batch(seed_qs)
            total, _ = db.get_question_count()
            print(f"已导入 {total} 道种子题目")

        # 单元过滤
        unit_filter = None
        if args.units:
            unit_filter = [int(u.strip()) for u in args.units.split(",")]

        # 题型过滤
        section_filter = None
        tag_filter = None
        if args.type:
            t = args.type.strip()
            if t == "图形" or t == "图形题":
                tag_filter = "图形"
            elif t in TYPE_MAP:
                section_filter = [TYPE_MAP[t]]

        builder = ExamBuilder(config, db)
        exam = builder.build_exam(
            week_label=args.week or "",
            unit_filter=unit_filter,
            section_filter=section_filter,
            tag_filter=tag_filter,
        )

        renderer = DocxRenderer(config)
        type_tag = f"_{args.type}" if args.type else ""
        output_name = args.output or f"{config.grade_name}{config.grade_term}_周末练习卷{type_tag}"
        if args.week:
            output_name += f"_第{args.week}周"
        output_name += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path = os.path.join(config.get_output_dir(), f"{output_name}.docx")

        filepath = renderer.render(exam, output_path)
        print(f"[OK] 试卷已生成: {filepath}")
        print(f"  标题: {exam.title}")
        print(f"  总分: {exam.total_score} 分 | 共 {exam.total_questions} 题")
        for section in exam.sections:
            print(f"  {section.title}: {len(section.questions)}题 / {section.total_score}分")


def cmd_status(args, config: ConfigManager):
    """查看题库统计"""
    with DBManager(config.get_db_path()) as db:
        total, by_section = db.get_question_count()
        units = db.get_available_units()

        print(f"题库路径: {config.get_db_path()}")
        print(f"题目总数: {total}")
        print(f"涵盖单元: {units}")
        print(f"\n按题型/难度分布:")
        print(f"{'题型':<16} {'难度1':>6} {'难度2':>6} {'难度3':>6} {'难度4':>6} {'难度5':>6} {'小计':>6}")
        print("-" * 58)

        section_names = {
            "oral_calc": "口算题", "fill_blank": "填空题", "choice": "选择题",
            "vertical_calc": "竖式/脱式", "word_problem": "解决问题",
        }
        for section_id, name in section_names.items():
            dist = by_section.get(section_id, {})
            subtotal = sum(dist.values())
            print(f"{name:<16} {dist.get(1,0):>6} {dist.get(2,0):>6} "
                  f"{dist.get(3,0):>6} {dist.get(4,0):>6} {dist.get(5,0):>6} {subtotal:>6}")


def cmd_seed(args, config: ConfigManager):
    """管理种子数据"""
    with DBManager(config.get_db_path()) as db:
        if args.reload:
            print("重置题库...")
            db.reset()
            seed_qs = get_all_seed_questions()
            db.insert_batch(seed_qs)
            total, _ = db.get_question_count()
            print(f"已重新导入 {total} 道种子题目")


def cmd_sync(args, config: ConfigManager):
    """手动触发题库更新（算法生成+网络抓取+本地导入）"""
    with DBManager(config.get_db_path()) as db:
        sync_cfg = config.get_sync_config()
        engine = SyncEngine(db, sync_cfg)

        if not sync_cfg.get("enabled", True):
            print("自动更新未启用（config.yaml 中 sync.enabled: false）")
            return

        print("正在更新题库...")
        result = engine.sync_once()
        parts = [f"算法生成: +{result['generated']}题"]
        if result['scraped'] > 0:
            parts.append(f"网络抓取: +{result['scraped']}题")
        if result['imported'] > 0:
            parts.append(f"本地导入: +{result['imported']}题")
        total = result["generated"] + result["scraped"] + result["imported"]
        print(f"[OK] 更新完成（总+{total}题）: {', '.join(parts)}")
        if result.get("error"):
            print(f"  警告: {result['error']}")


def main():
    parser = argparse.ArgumentParser(
        description="小学数学练习试卷生成系统 — 北师大版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py generate                    # 生成本周试卷
  python main.py generate --week 12          # 指定第12周
  python main.py generate --units 1,2,5      # 限定1、2、5单元
  python main.py status                      # 查看题库统计
  python main.py seed --reload               # 重置题库
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate
    gen = subparsers.add_parser("generate", help="生成试卷")
    gen.add_argument("--week", type=str, default="", help="周次标签")
    gen.add_argument("--units", type=str, default="", help="限定单元，逗号分隔（如 1,2,5）")
    gen.add_argument("--type", type=str, default="", help="限定题型（口算题/填空题/选择题/竖式/解决问题/图形题）")
    gen.add_argument("--output", type=str, default="", help="自定义输出文件名（不含扩展名）")

    # status
    subparsers.add_parser("status", help="查看题库统计")

    # seed
    seed = subparsers.add_parser("seed", help="题库种子管理")
    seed.add_argument("--reload", action="store_true", help="重置并重新导入种子数据")

    # sync
    subparsers.add_parser("sync", help="手动触发在线同步")

    # ui
    subparsers.add_parser("ui", help="启动图形化界面（Web UI）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # UI 命令不依赖 config 直接启动
    if args.command == "ui":
        from app import build_ui
        demo = build_ui()
        demo.launch(inbrowser=True, show_error=True)
        return

    config = ConfigManager()

    commands = {
        "generate": cmd_generate,
        "status": cmd_status,
        "seed": cmd_seed,
        "sync": cmd_sync,
    }
    commands[args.command](args, config)


if __name__ == "__main__":
    main()
