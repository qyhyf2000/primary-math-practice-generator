# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

小学数学练习试卷生成系统 — 北师大版二年级下册。自动生成含口算、填空、选择、竖式计算、应用题的 Word 试卷（.docx），支持图形题（角、钟面、立方体等）的表格+Unicode 渲染。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# CLI 生成试卷
python main.py generate                          # 全单元全题型
python main.py generate --week 12                # 指定周次
python main.py generate --units 1,2,5            # 限定单元
python main.py generate --type 图形题             # 限定题型（口算题/填空题/选择题/竖式/解决问题/图形题）

# 启动 Web UI
python main.py ui
# 或
python app.py

# 题库管理
python main.py status                            # 查看统计
python main.py sync                              # 手动触发更新（算法生成+网络抓取+本地导入）
python main.py seed --reload                     # 重置题库并重新导入种子数据
```

## 架构

```
config.yaml  →  ConfigManager
                   ↓
question_bank/  →  DBManager (SQLite)  ←  seed_data (内置169题)
                   ↓                      ←  question_generator (算法生成)
                   ↓                      ←  scrapers (无忧考网等抓取)
                   ↓                      ←  sync_engine (编排以上来源)
generator/     →  ExamBuilder  →  QuestionPicker (分层随机+排重)
                                    ↓
renderer/      →  DocxRenderer  →  section_renderers (普通题型)
                              →  graphics_renderer (图形题，表格+Unicode)
```

**4 层流水线：**
1. **ConfigManager** — 读取 `config.yaml`，年级/题型/难度/排版全部由配置驱动
2. **Question Bank** — SQLite 存储（`data/question_bank.db`），4 种来源：种子数据、算法生成、网络抓取、本地文件导入
3. **Generator** — `ExamBuilder` 按配置的题型结构组装试卷，`QuestionPicker` 做分层随机抽样（低难度40% + 高难度40% + 弹性20%）
4. **Renderer** — python-docx 生成 .docx，`section_renderers` 处理普通题型，`graphics_renderer` 处理图形题

## 关键约定

### 图形题的 tags 编码

图形题在 `tags` 字段中以 `graphic:` 前缀嵌入 JSON 渲染指令。`section_renderers._parse_graphic_info()` 负责解析，根据 `type` 字段路由到 `graphics_renderer` 中对应的渲染函数。

```python
# 种子数据中：
tags = "图形,数角,graphic:{\"type\":\"count_angles\",\"shapes\":[...]}"

# 算法生成器中：
tags = f"图形,数角,graphic:{json.dumps(graphic, ensure_ascii=False)}"
```

支持的 `type`：`angle_identify`, `angle_judge`, `count_angles`, `grid_count`, `draw_grid`, `draw_angle`, `clock`, `clock_time`, `cube_stack`, `cube_view`, `shape_classify`, `tangram`, `parallelogram`

### 排重机制

`DBManager.record_exam()` 将试卷中所有题目 ID 写入 `exam_history` 表。下次生成时 `get_recently_used_ids(weeks=N)` 排除最近 N 周内用过的题目。排重窗口由 `config.yaml` 中 `dedup_window_weeks` 控制（默认4周）。

### 题型过滤的两种模式

- `section_filter` — 按 section ID 过滤（如 `["oral_calc", "word_problem"]`），图形题会出现在其所属的 section 中
- `tag_filter` — 按标签过滤（如 `"图形"`），跨 section 搜索。用于"只出图形题"场景

### 数据库路径

`DBManager` 接受相对路径时相对于项目根目录。`ConfigManager.get_db_path()` 自动将 `config.yaml` 中的相对路径转为绝对路径。测试可用 `':memory:'`。

### 升年级时的修改点

1. `config.yaml` — 修改 `grade.name`、`grade.term`
2. `app.py` — 修改 `UNIT_NAMES` 字典
3. `src/question_bank/seed_data.py` — 更新种子题目
4. `src/question_bank/question_generator.py` — 调整 `RANGES` 数值范围和生成器列表

## 网络抓取

`scrapers.py` 支持无忧考网 (51test.net) 和瑞文网 (ruiwen.com)。内置重试机制和中文编码自动检测。`_extract_answer_section()` 尝试从页面中分离答案区域，`_parse_answer_list()` 将其解析为题号→答案的映射。`quick_test_scrape(url)` 可用于调试抓取效果。
