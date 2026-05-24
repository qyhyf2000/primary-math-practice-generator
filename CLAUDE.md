# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

小学数学练习试卷生成系统 — 北师大版二年级下册。CLI + Gradio Web UI，自动生成含口算、填空、选择、竖式计算、应用题的 Word 试卷（.docx）。图形题（角、钟面、立方体、网格）用 PIL 绘制后嵌入 Word。

## 常用命令

```bash
pip install -r requirements.txt

# CLI
python main.py generate                          # 全单元全题型
python main.py generate --week 12                # 指定周次
python main.py generate --units 1,2,5            # 限定单元
python main.py generate --type 图形题             # 限定题型
python main.py status                            # 题库统计
python main.py sync                              # 手动同步（算法生成+抓取+导入）
python main.py seed --reload                     # 重置并重导种子数据
python main.py ui                                # 启动 Gradio Web UI

# 测试
python -m pytest tests/ -v                       # 全部测试
python -m pytest tests/test_db_manager.py -v     # 单个测试文件
```

## 架构

```
config.yaml → ConfigManager
                  ↓
question_bank/  →  DBManager (SQLite)  ←  seed_data (内置168题)
                  ↓                      ←  question_generator (算法生成)
                  ↓                      ←  scrapers (无忧考网/瑞文网)
                  ↓                      ←  sync_engine (编排以上来源)
generator/     →  ExamBuilder → QuestionPicker (难度分层 + 使用次数分层)
                                    ↓
renderer/      →  DocxRenderer → section_renderers (普通题型 + 图形路由)
                              → graphics_renderer (PIL 绘制: 立方体/角/钟面/网格)
```

## 关键约定

### 选题层级机制（tier-based selection）

题目不再按时间窗口排除，而是按**历史使用次数**分 tier：tier 0（从未用过）→ 优先抽取，tier 1（用过1次）→ 次之，依此类推。所有题最终循环复用。

- `DBManager.get_questions_by_tier()` — LEFT JOIN `exam_history` 统计使用次数，按 tier ASC 排列
- `QuestionPicker._pick_by_tier()` — 从低 tier 逐级选取，同级内随机
- `DBManager.record_exam()` — 每次生成写入 `exam_history`，驱动下次 tier 计算

### 图形题的 tags 编码

图形题在 `tags` 字段中以 `graphic:` 前缀嵌入 JSON 渲染指令。section_renderers 中的 `_parse_graphic_info()` 解析，根据 `type` 路由到 `graphics_renderer` 对应函数。

```python
tags = "图形,立方体,graphic:{\"type\":\"cube_stack\",\"grid\":[[2,1],[1,0]]}"
```

支持的 `type` 及渲染方式：

| type | 渲染函数 | 方式 |
|------|---------|------|
| `angle_identify` | `render_angle_question` | PIL 120×120px 角图 |
| `angle_judge` | `render_shape_judge_question` | 表格+符号 |
| `count_angles` | `render_count_angles_question` | 表格+符号 |
| `grid_count` | `render_grid_count_question` | PIL 网格图 |
| `draw_grid` | `render_grid_count_question` | PIL 方格纸 |
| `draw_angle` | `render_angle_drawing` | 留白画角区 |
| `clock` | `render_clock_question` | PIL 钟面图 |
| `clock_time` | `render_clock_time_question` | PIL 空白钟面 |
| `cube_stack` | `render_cube_stack_question` | PIL 等轴测立体图 |
| `cube_view` | `render_cube_view_question` | 表格+符号 |
| `shape_classify` | `render_shape_classify_question` | 表格+Unicode |
| `tangram` | `render_tangram_question` | 着色表格 |
| `parallelogram` | `render_parallelogram_question` | 表格对比 |

### 题型过滤的两种模式

- `section_filter` — 按 section ID 过滤（如 `["oral_calc", "word_problem"]`），图形题出现在所属 section 中
- `tag_filter` — 按标签过滤（如 `"图形"`），跨 section 搜索，用于"只出图形题"场景

### 数据库

- SQLite，路径由 `config.yaml` → `question_bank.db_path` 配置
- `ConfigManager.get_db_path()` 相对于项目根目录解析
- `DBManager` 支持上下文管理器（`with DBManager(...) as db:`），测试可用 `':memory:'`

### 升年级时的修改点

1. `config.yaml` — 修改 `grade.name`、`grade.term`、`grade.units` 列表
2. `src/question_bank/seed_data.py` — 更新种子题目
3. `src/question_bank/question_generator.py` — 调整 `RANGES` 数值范围和生成器列表
