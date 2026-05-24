# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

小学数学练习试卷生成系统 — 北师大版 1-6 年级上下册（共 12 学期）。CLI + Gradio Web UI，自动生成含口算、填空、选择、竖式计算、应用题的 Word 试卷，图形题用 PIL 绘制嵌入。支持错题本、知识点专项突破、学习报告等家长功能。

## 常用命令

```bash
pip install -r requirements.txt

# CLI — 支持 --grade 1-6 --term 1-2
python main.py generate                                    # 默认二年级下册
python main.py generate --grade 3 --term 1 --week 5        # 三年级上册第5周
python main.py generate --grade 1 --term 1 --type 图形题    # 一年级上册图形题
python main.py status                                      # 题库统计
python main.py sync                                        # 手动同步（算法生成+抓取+导入）
python main.py seed --reload                               # 重置种子数据
python main.py ui                                          # 启动 Gradio Web UI

# 测试
python -m pytest tests/ -v
```

## 架构

```
config.yaml → ConfigManager (12学期单元配置，set_active切换上下文)
                  ↓
question_bank/ → DBManager (SQLite, grade+term列, 自动迁移)
                  ↓  ← seed_data (内置168题, 仅二下)
                  ↓  ← question_generator (GradeProfile + 注册表, ~70生成器)
                  ↓  ← sync_engine + scrapers
                  ↓  ← wrong_answer_manager (错题本)
generator/     → ExamBuilder → QuestionPicker (使用次数tier分层 + 难度分层)
                                    ↓
renderer/      → DocxRenderer → section_renderers (文字题型+图形路由)
                              → graphics_renderer (PIL绘制: 角/钟面/立方体/七巧板等)
report_generator.py → 学习周报 docx
```

## 关键约定

### 年级/学期切换

```python
config.set_active(grade=3, term=1)  # 切换到三年级上册
config.get_units()                   # 返回三年级上册的单元映射
```

CLI: `--grade 3 --term 1`, UI: 年级下拉框 + 学期单选。

### GradeProfile 和生成器注册表

`question_generator.py` 使用能力注册表模式。每个生成器注册时带条件 lambda：

```python
_register("oral_calc", _gen_oral_mult_table,
    lambda p: p.supports_multiplication and p.times_table_max > 0)
```

`generate_questions(count, grade, term)` 自动筛选适用生成器。新增生成器只需添加函数 + 注册，无需修改入口逻辑。

### 选题层级机制

`DBManager.get_questions_by_tier()` 按题目历史使用次数（tier）升序排列，优先选从未用过的题，所有题循环复用。

### 图形题的 tags 编码

图形题在 `tags` 中以 `graphic:{JSON}` 编码。`section_renderers._parse_graphic_info()` 解析，按 `type` 路由到 `graphics_renderer` 对应函数。全部 13 种图形类型用 PIL 绘制。

### 数据库

- SQLite，`questions` 表含 `grade`/`term` 列，自动迁移旧库
- `DBManager` 支持上下文管理器 `with DBManager(...) as db:`
- 新年级首次使用自动生成 100 题补充题库
- 测试用 `':memory:'` 模式

### 升年级/加单元

1. `config.yaml` → `curriculum` 段添加/修改单元列表
2. `question_generator.py` → 添加新生成器 + `_register()` 注册
3. `PROFILES` → 调整 `GradeProfile` 参数控制知识边界

### 错题本

`wrong_answer_manager.py` — 独立 SQLite 表 `wrong_answers`。UI 支持录入错题、统计、生成重练卷（含答案，自动标记已复习）。

### 打印友好模式

`DocxRenderer.render_with_answer()` — 学生版 + 参考答案分页输出。

## 关键文件

| 文件 | 行数 | 用途 |
|------|------|------|
| `config.yaml` | ~160 | 12学期单元 + 试卷结构 + 排版配置 |
| `src/config/config_manager.py` | ~130 | 配置加载, set_active, get_curriculum |
| `src/question_bank/question_generator.py` | ~1700 | GradeProfile + 注册表 + ~70生成器 |
| `src/question_bank/db_manager.py` | ~300 | SQLite CRUD + 迁移 + tier查询 |
| `src/question_bank/seed_data.py` | ~730 | 168道二下种子题 |
| `src/renderer/graphics_renderer.py` | ~1200 | PIL 13种图形渲染 |
| `src/renderer/section_renderers.py` | ~280 | 题型渲染 + graphic路由 |
| `src/wrong_answer_manager.py` | ~80 | 错题本管理 |
| `src/report_generator.py` | ~90 | 学习周报生成 |
| `app.py` | ~530 | Gradio Web UI (4个Tab) |
| `main.py` | ~230 | CLI 入口 |
