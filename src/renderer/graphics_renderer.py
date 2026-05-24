"""
图形题渲染器 — 用表格和Unicode字符在Word文档中绘制小学数学几何图形

支持的类型：
- angle: 角的识别（直角/锐角/钝角）
- count_angles: 数图形中的角
- count_rects: 数长方形/正方形个数
- shape_identify: 图形识别（长方形/正方形/平行四边形）
- grid_count: 网格中的图形计数
- clock: 钟面读时（PIL 绘制圆形钟面）
"""
import math
from io import BytesIO
from PIL import Image, ImageDraw

from docx.shared import Cm, Pt, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .layout import (
    set_cjk_font, set_cell_border, cell_add_run,
    set_table_borders, set_cell_shading,
)

FONT = "宋体"
BODY_SIZE = 12


def _draw_angle_image(angle_type: str, size: int = 120) -> BytesIO:
    """
    用 PIL 绘制单个角的图形。

    angle_type: "直角" / "锐角" / "钝角"
    size: 图片像素尺寸
    """
    import math as _math
    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size - 20  # 顶点在底部中央
    ray_len = size - 50
    lw = 3  # 线宽

    if angle_type == "直角":
        angle_deg = 90
    elif angle_type == "锐角":
        angle_deg = 50
    else:  # 钝角
        angle_deg = 130

    # 水平射线（向右）
    end_h = (cx + ray_len, cy)
    # 另一条射线（按角度逆时针旋转）
    rad = _math.radians(angle_deg)
    end_a = (cx - int(ray_len * _math.cos(rad)),
             cy - int(ray_len * _math.sin(rad)))

    draw.line([end_a, (cx, cy), end_h], fill=(60, 60, 60), width=lw)

    # 画角度弧线
    arc_r = 22
    if angle_type == "直角":
        # 直角标记：小正方形
        sq = 14
        draw.rectangle([cx, cy - sq, cx + sq, cy], outline=(60, 60, 60), width=2)
    else:
        # 弧线
        start_angle = 0
        end_angle = -angle_deg
        bbox = [cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r]
        draw.arc(bbox, start=end_angle, end=0, fill=(60, 60, 60), width=2)

    # 画顶点小圆点
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(60, 60, 60))

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def render_angle_question(doc, q_num: int, q_content: str, angles: list):
    """
    渲染角的识别题 —— 用 PIL 绘制清晰的角图形。

    angles: [{"symbol": "╲", "label": "第1个"}, ...]
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 用表格排列角图形
    table = doc.add_table(rows=2, cols=len(angles))
    table.alignment = 1
    set_table_borders(table, val="none")

    # 映射 symbol → 角类型
    SYMBOL_TO_TYPE = {
        "┌": "直角", "∟": "直角",
        "∠": "锐角", "╱": "锐角",
        "╲": "钝角", "╱ ": "钝角",
    }

    for i, angle_info in enumerate(angles):
        symbol = angle_info.get("symbol", "∠")
        label = angle_info.get("label", f"第{i+1}个")
        angle_type = SYMBOL_TO_TYPE.get(symbol, "锐角")

        # 图片行
        cell_img = table.cell(0, i)
        cell_img.width = Cm(3.0)
        p_img = cell_img.paragraphs[0]
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_buf = _draw_angle_image(angle_type)
        run_img = p_img.add_run()
        run_img.add_picture(img_buf, width=Cm(2.5))

        # 标签行
        cell_lbl = table.cell(1, i)
        p_lbl = cell_lbl.paragraphs[0]
        p_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_lbl = p_lbl.add_run(f"({label})")
        set_cjk_font(run_lbl, FONT, 10)

    doc.add_paragraph()


def render_count_angles_question(doc, q_num: int, q_content: str, shapes: list):
    """
    渲染数角题。

    shapes: [("三角形(图)", 3), ("长方形(图)", 4), ...]
    每个元素为 (形状描述或Unicode, 角的个数)
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 用表格渲染图形
    cols = len(shapes)
    table = doc.add_table(rows=2, cols=cols)
    table.alignment = 1
    set_table_borders(table, val="single", sz="4")

    for i, (shape_str, count) in enumerate(shapes):
        # 图形行
        cell_shape = table.cell(0, i)
        p = cell_shape.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(shape_str)
        set_cjk_font(run, FONT, 22 if len(shape_str) <= 5 else 14)

        # 答案行
        cell_ans = table.cell(1, i)
        p2 = cell_ans.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run2 = p2.add_run(f"(    )个角")
        set_cjk_font(run2, FONT, 10)

    doc.add_paragraph()


def _draw_grid_image(rows: int, cols: int, cell_size: int = 60) -> BytesIO:
    """
    用 PIL 绘制清晰的方格网格图。

    cell_size: 每格像素大小
    """
    lw = 2  # 线宽
    w = cols * cell_size + lw
    h = rows * cell_size + lw

    img = Image.new('RGB', (w, h), 'white')
    draw = ImageDraw.Draw(img)

    # 画横线
    for r in range(rows + 1):
        y = r * cell_size
        draw.line([(0, y), (w, y)], fill=(40, 40, 40), width=lw)

    # 画竖线
    for c in range(cols + 1):
        x = c * cell_size
        draw.line([(x, 0), (x, h)], fill=(40, 40, 40), width=lw)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def render_grid_count_question(doc, q_num: int, q_content: str,
                               rows: int, cols: int, answer: str = "",
                               description: str = ""):
    """
    渲染网格图形计数题 —— 用 PIL 绘制清晰网格。

    绘制一个 rows x cols 的完整网格，下方留空作答。
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 生成网格图片并嵌入
    img_buf = _draw_grid_image(rows, cols)
    if img_buf:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_buf, width=Cm(6))

    # 题目内容已包含填空括号，下方仅放网格图即可
    doc.add_paragraph()


def render_shape_judge_question(doc, q_num: int, q_content: str, shapes: list):
    """
    渲染图形判断/分类题。

    shapes: [("△", "①"), ("□", "②"), ...]
    第一行显示图形符号，第二行显示编号+括号供作答。
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    cols = len(shapes)
    table = doc.add_table(rows=2, cols=cols)
    table.alignment = 1
    set_table_borders(table, val="single", sz="4")

    for i, (symbol, label) in enumerate(shapes):
        # 图形符号行
        cell_shape = table.cell(0, i)
        cell_shape.width = Cm(2.5)
        p1 = cell_shape.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(6)
        p1.paragraph_format.space_after = Pt(6)
        run1 = p1.add_run(symbol)
        set_cjk_font(run1, FONT, 22 if len(symbol) <= 3 else 14)

        # 编号 + 作答行
        cell_ans = table.cell(1, i)
        p2 = cell_ans.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(2)
        p2.paragraph_format.space_after = Pt(4)
        run2 = p2.add_run(f"{label} (    )")
        set_cjk_font(run2, FONT, 10)

    doc.add_paragraph()


def render_shape_classify_question(doc, q_num: int, q_content: str, shapes: list):
    """
    渲染图形分类/命名题——显示图形，学生在下方写图形名称。

    shapes: [("△", ""), ("□", ""), ("▱", ""), ...]
    第二行留空供学生写名称。
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    cols = len(shapes)
    table = doc.add_table(rows=2, cols=cols)
    table.alignment = 1
    set_table_borders(table, val="single", sz="4")

    for i, (symbol, label) in enumerate(shapes):
        # 图形符号行
        cell_shape = table.cell(0, i)
        cell_shape.width = Cm(2.5)
        p1 = cell_shape.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(6)
        p1.paragraph_format.space_after = Pt(6)
        run1 = p1.add_run(symbol)
        set_cjk_font(run1, FONT, 22 if len(symbol) <= 3 else 14)

        # 名称填空行
        cell_ans = table.cell(1, i)
        p2 = cell_ans.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(4)
        p2.paragraph_format.space_after = Pt(6)
        label_text = label if label else f"图形{i + 1}"
        run2 = p2.add_run(f"{label_text}: __________")
        set_cjk_font(run2, FONT, 10)

    doc.add_paragraph()


def render_tangram_question(doc, q_num: int, q_content: str,
                            grid: list, pieces: list = None):
    """
    渲染七巧板拼图题——用着色表格模拟七巧板拼出的图案。

    grid: 7x7 的二维数组，每个元素是颜色代码或0（空白）
          'r'=红, 'b'=蓝, 'g'=绿, 'y'=黄, 'p'=紫, 'o'=橙, 'c'=青
    pieces: [(形状名, 颜色码), ...] 七巧板的7块信息
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    color_map = {
        'r': "FF6B6B", 'b': "4ECDC4", 'g': "96CEB4",
        'y': "FFEAA7", 'p': "DDA0DD", 'o': "FFB347",
        'c': "87CEEB", 0: "FFFFFF",
    }

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = 1
    set_table_borders(table, val="single", sz="6")

    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.width = Cm(0.7)
            color_code = grid[r][c]
            color_hex = color_map.get(color_code, "FFFFFF")
            if color_hex != "FFFFFF":
                set_cell_shading(cell, color_hex)
            # 空内容撑起高度
            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_before = Pt(2)
            cp.paragraph_format.space_after = Pt(2)
            run_c = cp.add_run(" ")
            set_cjk_font(run_c, FONT, 6)

    # 问题区
    if pieces:
        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_before = Pt(6)
        p_info.paragraph_format.space_after = Pt(2)
        pieces_text = "七巧板由以下7块组成：" + "、".join(
            f"{name}({code})" for name, code in pieces
        )
        run_info = p_info.add_run(pieces_text)
        set_cjk_font(run_info, FONT, 9)

    doc.add_paragraph()


def render_parallelogram_question(doc, q_num: int, q_content: str):
    """
    渲染平行四边形变形题——展示长方形拉成平行四边形的过程。

    用两个表格并排对比：长方形(4个直角标记) vs 平行四边形(锐角+钝角)。
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 两个图形并排
    table = doc.add_table(rows=1, cols=2)
    table.alignment = 1
    set_table_borders(table, val="none")

    # 左：长方形
    left_cell = table.cell(0, 0)
    left_cell.width = Cm(5.0)
    inner_left = left_cell.add_table(rows=3, cols=5)
    set_table_borders(inner_left, val="single", sz="4")
    # 长方形轮廓（用■填充四角表示直角）
    left_shape = [
        ["■", "", "", "", "■"],
        [" ", "", "", "", " "],
        ["■", "", "", "", "■"],
    ]
    for r in range(3):
        for c in range(5):
            cc = inner_left.cell(r, c)
            cc.width = Cm(0.8)
            cp = cc.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            txt = left_shape[r][c]
            if txt == "■":
                run_l = cp.add_run("∟")
                set_cjk_font(run_l, FONT, 10)
            else:
                run_l = cp.add_run("  ")
                set_cjk_font(run_l, FONT, 8)
    # 标注
    p_left = left_cell.add_paragraph()
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_left.paragraph_format.space_before = Pt(4)
    run_l = p_left.add_run("长方形")
    set_cjk_font(run_l, FONT, 10)

    # 箭头
    # (arrow is implicit in the layout)

    # 右：平行四边形
    right_cell = table.cell(0, 1)
    right_cell.width = Cm(5.0)
    inner_right = right_cell.add_table(rows=3, cols=5)
    set_table_borders(inner_right, val="single", sz="4")
    right_shape = [
        [" ", "", "", "■", ""],
        [" ", "", "", "", " "],
        [" ", "■", "", "", ""],
    ]
    for r in range(3):
        for c in range(5):
            cc = inner_right.cell(r, c)
            cc.width = Cm(0.8)
            cp = cc.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            txt = right_shape[r][c]
            if txt == "■":
                run_r = cp.add_run("∠")
                set_cjk_font(run_r, FONT, 10)
            else:
                run_r = cp.add_run("  ")
                set_cjk_font(run_r, FONT, 8)

    p_right = right_cell.add_paragraph()
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_right.paragraph_format.space_before = Pt(4)
    run_r = p_right.add_run("平行四边形")
    set_cjk_font(run_r, FONT, 10)

    doc.add_paragraph()


def render_angle_drawing(doc, q_num: int, q_content: str):
    """渲染画角题 — 留空白让学生画指定的角"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 留3行空白用于画角
    for _ in range(3):
        blank_p = doc.add_paragraph()
        blank_p.paragraph_format.space_before = Pt(0)
        blank_p.paragraph_format.space_after = Pt(0)
        run = blank_p.add_run(" " * 60)
        set_cjk_font(run, FONT, BODY_SIZE)


# ============================================================
# 图形符号映射
# ============================================================

# 基础形状
SHAPES = {
    "直角": "∟",
    "锐角": "∠",
    "钝角": "⦥",      # 可用 > 替代
    "三角形": "△",
    "正方形": "□",
    "长方形": "▭",
    "平行四边形": "▱",
    "圆形": "○",
    "五边形": "⬠",
    "六边形": "⬡",
    "交叉": "╳",
    "点": "●",
}

# 角的图标（用于识别题）
ANGLE_ICONS = {
    "直角": "┌",
    "锐角": "∠",
    "钝角": "╲",
}

# 多边形用于数角
POLYGONS_FOR_COUNT = [
    ("△\n三角形", 3),
    ("□\n正方形", 4),
    ("▭\n长方形", 4),
    ("▱\n平行四边形", 4),
    ("⬠\n五边形", 5),
]


# ============================================================
# 钟面图形渲染
# ============================================================

def _draw_clock_image(hour: int, minute: int, second: int = 0,
                       draw_hands: bool = True, size: int = 200) -> BytesIO:
    """
    用 PIL 绘制圆形钟面，返回 PNG 的 BytesIO。

    参数：
        hour: 小时 (0-12)
        minute: 分钟 (0-59)
        second: 秒 (0-59, 默认 0)
        draw_hands: 是否绘制指针（False=空白钟面供学生画）
        size: 图片像素尺寸（默认 200）
    """
    cx = cy = size // 2
    r = int(size * 0.45)

    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)

    # 1. 外圆
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline='#333', width=3)

    # 2. 刻度线（60根，正点加粗加长）
    for i in range(60):
        angle_rad = (i * 6 - 90) * math.pi / 180
        is_hour = (i % 5 == 0)
        outer = r - 3
        inner = outer - (12 if is_hour else 6)
        x1 = cx + inner * math.cos(angle_rad)
        y1 = cy + inner * math.sin(angle_rad)
        x2 = cx + outer * math.cos(angle_rad)
        y2 = cy + outer * math.sin(angle_rad)
        draw.line([(x1, y1), (x2, y2)], fill='#333', width=2 if is_hour else 1)

    # 3. 数字 1-12
    for num in range(1, 13):
        angle_rad = (num * 30 - 90) * math.pi / 180
        nr = r - 22
        nx = cx + nr * math.cos(angle_rad)
        ny = cy + nr * math.sin(angle_rad)
        # 用矩形近似文字位置（Pillow 默认字体太小，用较大偏移）
        draw.text((nx - 5, ny - 6), str(num), fill='#333')

    if draw_hands:
        # 4. 时针（短粗，圆头）
        h_angle = ((hour % 12) * 30 + minute * 0.5 - 90) * math.pi / 180
        hx = cx + 38 * math.cos(h_angle)
        hy = cy + 38 * math.sin(h_angle)
        draw.line([(cx, cy), (hx, hy)], fill='#1a1a1a', width=4)

        # 5. 分针（细长，尖头）
        m_angle = (minute * 6 + second * 0.1 - 90) * math.pi / 180
        mx = cx + 58 * math.cos(m_angle)
        my = cy + 58 * math.sin(m_angle)
        draw.line([(cx, cy), (mx, my)], fill='#1a1a1a', width=2)

        # 6. 秒针（最细最长，红色，带尾针）
        s_angle = (second * 6 - 90) * math.pi / 180
        sx = cx + 68 * math.cos(s_angle)
        sy = cy + 68 * math.sin(s_angle)
        # 尾针（反向延伸 15px）
        tx = cx - 15 * math.cos(s_angle)
        ty = cy - 15 * math.sin(s_angle)
        draw.line([(tx, ty), (sx, sy)], fill='#cc0000', width=1)

        # 7. 中心帽（覆盖三针交汇点）
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill='#222')

        # 8. 秒针尾端小红点
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill='#cc0000')

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def render_clock_question(doc, q_num: int, q_content: str, clocks: list):
    """
    渲染钟面读时题。

    clocks: [{"hour": 3, "minute": 0}, ...]
    每个钟面用 PIL 绘制圆形钟面图片，嵌入 Word。
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    cols = min(len(clocks), 4)
    outer = doc.add_table(rows=2, cols=cols)
    outer.alignment = 1
    set_table_borders(outer, val="none")

    for ci, clock in enumerate(clocks):
        h = clock.get("hour", 0) % 12
        if h == 0:
            h = 12
        m = clock.get("minute", 0)
        s = clock.get("second", 0)

        # 图片行
        img_cell = outer.cell(0, ci)
        set_cell_border(img_cell, top="none", bottom="none", left="none", right="none")
        img_cell.width = Cm(3.0)
        img_buf = _draw_clock_image(h, m, s, draw_hands=True)
        p_img = img_cell.paragraphs[0]
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_buf, width=Cm(2.5))

        # 答案行
        ans_cell = outer.cell(1, ci)
        set_cell_border(ans_cell, top="none", bottom="none", left="none", right="none")
        p_ans = ans_cell.paragraphs[0]
        p_ans.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ans.paragraph_format.space_before = Pt(2)
        p_ans.paragraph_format.space_after = Pt(4)
        run_ans = p_ans.add_run(f"钟面{ci + 1}: __时__分")
        set_cjk_font(run_ans, FONT, 9)

    doc.add_paragraph()


def render_clock_time_question(doc, q_num: int, q_content: str,
                               times: list):
    """
    渲染钟面时间题——给出文字+空白钟面，让学生画时针分针。

    times: [("3:00", "3时"), ("7:30", "7时30分"), ...]
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    cols = min(len(times), 4)
    table = doc.add_table(rows=2, cols=cols)
    table.alignment = 1
    set_table_borders(table, val="single", sz="4")

    for ci, (time_str, label) in enumerate(times):
        # 时间标签行
        cell_label = table.cell(0, ci)
        cell_label.width = Cm(3.0)
        pl = cell_label.paragraphs[0]
        pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_l = pl.add_run(f"{label}\n({time_str})")
        set_cjk_font(run_l, FONT, 9)

        # 空白钟面图片
        cell_draw = table.cell(1, ci)
        cell_draw.width = Cm(3.0)
        pd = cell_draw.paragraphs[0]
        pd.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pd.paragraph_format.space_before = Pt(4)
        pd.paragraph_format.space_after = Pt(4)
        img_buf = _draw_clock_image(0, 0, 0, draw_hands=False)
        run_d = pd.add_run()
        run_d.add_picture(img_buf, width=Cm(2.5))

    doc.add_paragraph()


# ============================================================
# 立方体堆叠渲染
# ============================================================

def _draw_isometric_cubes(grid: list, a: int = 36, b: int = 18,
                          h: int = 32) -> BytesIO:
    """
    用 PIL 绘制等轴测立体立方体堆叠图。

    参数：
        grid: 二维数组，grid[r][c] = 该位置的立方体层数
        a: 顶部菱形半宽（像素）
        b: 顶部菱形半高（像素）
        h: 立方体高度（像素）

    三个可见面配色：
        顶面 — 最亮，左侧面 — 中等，右侧面 — 最暗
    绘制顺序从远到近、从下到上，保证遮挡正确。
    """
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    if rows == 0 or cols == 0:
        return BytesIO()

    max_layers = max(max(row) for row in grid)

    # 计算图片尺寸
    margin = 40
    img_w = (rows + cols) * a + margin * 2
    img_h = max_layers * h + (rows + cols) * b + h + margin * 2

    origin_x = img_w // 2
    origin_y = margin + max_layers * h + b

    img = Image.new('RGB', (img_w, img_h), 'white')
    draw = ImageDraw.Draw(img)

    # 收集所有需要绘制的立方体，按深度排序
    cubes = []
    for r in range(rows):
        for c in range(cols):
            for l in range(grid[r][c]):
                cubes.append((r, c, l))

    # 排序：低层先画，(row+col) 小的（远的）先画
    cubes.sort(key=lambda x: (x[2], x[0] + x[1]))

    # 三种面的颜色（打印友好的灰度梯度）
    color_top = (230, 238, 250)     # 顶面 — 最亮
    color_left = (170, 195, 225)    # 左侧面 — 中等
    color_right = (125, 155, 195)   # 右侧面 — 最暗
    color_outline = (70, 70, 70)    # 边线

    for r, c, l in cubes:
        # 顶部菱形中心
        cx = origin_x + (c - r) * a
        cy = origin_y + (r + c) * b - l * h

        # 顶部菱形四个顶点
        top_pt = (cx, cy - b)           # 上
        right_pt = (cx + a, cy)         # 右
        bottom_pt = (cx, cy + b)        # 下
        left_pt = (cx - a, cy)          # 左

        # 左侧面：左→下→下+h→左+h
        left_face = [left_pt, bottom_pt,
                     (cx, cy + b + h), (cx - a, cy + h)]
        # 右侧面：右→下→下+h→右+h
        right_face = [right_pt, bottom_pt,
                      (cx, cy + b + h), (cx + a, cy + h)]
        # 顶面菱形
        top_face = [top_pt, right_pt, bottom_pt, left_pt]

        # 绘制面
        draw.polygon(left_face, fill=color_left, outline=color_outline)
        draw.polygon(right_face, fill=color_right, outline=color_outline)
        draw.polygon(top_face, fill=color_top, outline=color_outline)

        # 顶面十字线（增强立体感）
        draw.line([top_pt, bottom_pt], fill=color_outline, width=1)
        draw.line([left_pt, right_pt], fill=color_outline, width=1)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def render_cube_stack_question(doc, q_num: int, q_content: str,
                               grid: list, answer: str = ""):
    """
    渲染立方体堆叠计数题 —— 使用等轴测立体图。

    grid: 二维数组，grid[r][c] = 该位置的立方体层数
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 生成等轴测立体图并嵌入 Word
    img_buf = _draw_isometric_cubes(grid)
    if img_buf:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(6)
        run_img = p_img.add_run()
        run_img.add_picture(img_buf, width=Cm(7))

    # 问题作答区
    p_ans = doc.add_paragraph()
    p_ans.paragraph_format.space_before = Pt(4)
    run_ans = p_ans.add_run(f"一共有（    ）个小立方体。")
    set_cjk_font(run_ans, FONT, BODY_SIZE)

    doc.add_paragraph()


def render_cube_view_question(doc, q_num: int, q_content: str,
                              front_view: list, side_view: list,
                              top_view: list = None):
    """
    渲染三视图立方体计数题。

    front_view: 正面看每列最高层数，如 [3, 2, 1]
    side_view: 侧面看每列最高层数，如 [2, 1, 1]
    top_view: 俯视图网格（可选）
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{q_num}. {q_content}")
    set_cjk_font(run, FONT, BODY_SIZE)

    # 用表格展示三视图
    view_table = doc.add_table(rows=1, cols=3)
    view_table.alignment = 1
    set_table_borders(view_table, val="single", sz="4")

    views = [
        ("从正面看", front_view, "▯"),
        ("从侧面看", side_view, "▯"),
        ("从上面看", top_view or [], "▯"),
    ]

    for vi, (label, view, symbol) in enumerate(views):
        cell = view_table.cell(0, vi)
        cell.width = Cm(4.0)

        # 标题
        p_title = cell.paragraphs[0]
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_t = p_title.add_run(label)
        set_cjk_font(run_t, FONT, 9)

        # 画出视图（柱状）
        if view:
            max_h = max(view)
            inner = cell.add_table(rows=max_h + 1, cols=len(view))
            set_table_borders(inner, val="single", sz="4")
            for col_i, height in enumerate(view):
                for row_i in range(max_h):
                    r_inner = max_h - 1 - row_i
                    cc = inner.cell(r_inner, col_i)
                    cc.width = Cm(0.8)
                    if row_i < height:
                        set_cell_shading(cc, "B4C6E7")
                    p_inner = cc.paragraphs[0]
                    p_inner.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run_inner = p_inner.add_run("■" if row_i < height else " ")
                    set_cjk_font(run_inner, FONT, 8)
            # 底部标注
            for col_i in range(len(view)):
                cc_bottom = inner.cell(max_h, col_i)
                p_b = cc_bottom.paragraphs[0]
                p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_b = p_b.add_run(str(view[col_i]))
                set_cjk_font(run_b, FONT, 8)

    doc.add_paragraph()
    p_ans = doc.add_paragraph()
    run_ans = p_ans.add_run("一共有（    ）个小立方体。")
    set_cjk_font(run_ans, FONT, BODY_SIZE)
    doc.add_paragraph()
