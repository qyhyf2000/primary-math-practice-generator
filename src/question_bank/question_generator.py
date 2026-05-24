"""
算法题目生成器 — 自动生成小学数学题

覆盖题型：口算、填空、选择、竖式计算、应用题（含模板）
每次调用生成不重复的新题，确保题库持续增长。
"""
import random
import json
from typing import List
from .models import Question

# 二年级下册数值范围
RANGES = {
    "divisor": (2, 9),          # 除数范围
    "quotient": (2, 9),         # 商范围
    "remainder": (1, 4),        # 余数范围
    "multiplicand": (2, 9),     # 乘数
    "add_3digit": (100, 999),   # 三位数加法
    "sub_3digit": (100, 800),   # 三位数减法
}


def _rand(a, b):
    return random.randint(a, b)


# ============================================================
# 一、口算题生成 (oral_calc)
# ============================================================

def _gen_oral_div_table(diff: int) -> Question:
    """表内除法口算"""
    b = _rand(*RANGES["divisor"])
    c = _rand(*RANGES["quotient"])
    a = b * c
    return Question(
        unit=1, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} =",
        answer=str(c),
        knowledge_point="表内除法", tags="口算,除法",
        source="generated",
    )


def _gen_oral_div_remainder(diff: int) -> Question:
    """有余数除法口算"""
    b = _rand(3, 8)
    c = _rand(2, 9)
    r = _rand(1, b - 1)
    a = b * c + r
    return Question(
        unit=1, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} =",
        answer=f"{c}...{r}",
        knowledge_point="有余数除法", tags="口算,余数",
        source="generated",
    )


def _gen_oral_mix_mult_add(diff: int) -> Question:
    """乘加混合口算"""
    a = _rand(2, 9)
    b = _rand(2, 9)
    c = _rand(10, 60) if diff >= 2 else _rand(5, 20)
    return Question(
        unit=2, section="oral_calc", difficulty=diff,
        content=f"{a} × {b} + {c} =",
        answer=str(a * b + c),
        knowledge_point="乘加混合", tags="口算,混合运算",
        source="generated",
    )


def _gen_oral_mix_div_sub(diff: int) -> Question:
    """除减混合口算"""
    b = _rand(2, 9)
    c = _rand(2, 9)
    a = b * c
    d = _rand(2, 9) if diff >= 2 else _rand(1, 5)
    return Question(
        unit=2, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} - {d} =",
        answer=str(c - d),
        knowledge_point="除减混合", tags="口算,混合运算",
        source="generated",
    )


def _gen_oral_mix_paren(diff: int) -> Question:
    """带括号口算"""
    a = _rand(10, 50)
    b = _rand(2, 20)
    c = _rand(2, 5)
    op = "+" if random.random() > 0.5 else "-"
    if op == "+":
        result = (a + b) // c
        expr = f"({a} + {b}) ÷ {c}"
    else:
        # 确保整除
        if diff <= 2:
            c = _rand(2, 5)
            result = _rand(3, 9)
            a = _rand(result * c + 5, result * c + 30)
            b = a - result * c
        else:
            a = _rand(30, 80)
            b = _rand(2, 20)
            c = _rand(2, 5)
            result = (a - b) // c
            a = b + result * c  # 修正确保整除
        expr = f"({a} - {b}) ÷ {c}"
    return Question(
        unit=2, section="oral_calc", difficulty=max(diff, 2),
        content=f"{expr} =",
        answer=str(result),
        knowledge_point="括号运算", tags="口算,括号",
        source="generated",
    )


def _gen_oral_length(diff: int) -> Question:
    """长度单位换算口算"""
    conversions = [
        (5, "dm", "cm", 50), (8, "dm", "cm", 80),
        (3, "km", "m", 3000), (6, "km", "m", 6000),
        (40, "mm", "cm", 4), (80, "mm", "cm", 8),
        (200, "cm", "m", 2), (500, "cm", "m", 5),
        (2, "m", "cm", 200), (7, "m", "cm", 700),
    ]
    val, u1, u2, ans = random.choice(conversions)
    return Question(
        unit=4, section="oral_calc", difficulty=diff,
        content=f"{val} {u1} = ( ) {u2}",
        answer=str(ans),
        knowledge_point="长度换算", tags="口算,单位换算",
        source="generated",
    )


def _gen_oral_3digit_add(diff: int) -> Question:
    """三位数加法口算"""
    a = _rand(*RANGES["add_3digit"])
    b = _rand(100, 600)
    carry = (a % 10 + b % 10 >= 10) if diff >= 2 else True
    if carry and diff >= 2:
        a = _rand(200, 500)
        b = _rand(300, 600)
    return Question(
        unit=5, section="oral_calc", difficulty=diff,
        content=f"{a} + {b} =",
        answer=str(a + b),
        knowledge_point="三位数加法", tags="口算,加法",
        source="generated",
    )


def _gen_oral_3digit_sub(diff: int) -> Question:
    """三位数减法口算"""
    a = _rand(300, 999)
    b = _rand(100, a - 50)
    return Question(
        unit=5, section="oral_calc", difficulty=diff,
        content=f"{a} - {b} =",
        answer=str(a - b),
        knowledge_point="三位数减法", tags="口算,减法",
        source="generated",
    )


def _gen_oral_time(diff: int) -> Question:
    """时间换算口算"""
    conversions = [
        ("2 时 = ( ) 分", "120"),
        ("3 时 = ( ) 分", "180"),
        ("1 时 15 分 = ( ) 分", "75"),
        ("1 时 30 分 = ( ) 分", "90"),
        ("120 秒 = ( ) 分", "2"),
        ("3 分 = ( ) 秒", "180"),
        ("1 分 40 秒 = ( ) 秒", "100"),
        ("90 分 = ( ) 时 ( ) 分", "1时30分"),
    ]
    content, answer = random.choice(conversions)
    return Question(
        unit=7, section="oral_calc", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="时间换算", tags="口算,时分秒",
        source="generated",
    )


ORAL_GENERATORS = [
    (_gen_oral_div_table, 1),
    (_gen_oral_div_table, 2),
    (_gen_oral_div_remainder, 2),
    (_gen_oral_div_remainder, 3),
    (_gen_oral_mix_mult_add, 1),
    (_gen_oral_mix_mult_add, 2),
    (_gen_oral_mix_div_sub, 2),
    (_gen_oral_mix_paren, 2),
    (_gen_oral_mix_paren, 3),
    (_gen_oral_length, 1),
    (_gen_oral_length, 2),
    (_gen_oral_3digit_add, 1),
    (_gen_oral_3digit_add, 2),
    (_gen_oral_3digit_sub, 2),
    (_gen_oral_time, 1),
    (_gen_oral_time, 2),
]


# ============================================================
# 二、填空题生成 (fill_blank)
# ============================================================

def _gen_fb_remainder_relation(diff: int) -> Question:
    """余数与除数关系"""
    d = _rand(4, 8)
    max_r = d - 1
    possible = ", ".join(str(i) for i in range(1, max_r + 1))
    return Question(
        unit=1, section="fill_blank", difficulty=diff,
        content=f"一个数除以 {d}，余数可能是（    ），余数最大是（    ）。",
        answer=f"{possible}；{max_r}",
        knowledge_point="余数与除数关系", tags="填空,余数",
        source="generated",
    )


def _gen_fb_find_dividend(diff: int) -> Question:
    """已知除数商余数求被除数"""
    d = _rand(3, 8)
    q = _rand(3, 9)
    r = _rand(1, d - 1)
    dividend = d * q + r
    return Question(
        unit=1, section="fill_blank", difficulty=diff,
        content=f"在（   ）÷ {d} = {q} …… {r} 中，被除数是（   ）。",
        answer=str(dividend),
        knowledge_point="有余数除法逆向", tags="填空,逆向",
        source="generated",
    )


def _gen_fb_mix_order(diff: int) -> Question:
    """混合运算顺序"""
    a = _rand(20, 60)
    b = _rand(2, 9)
    c = _rand(2, 9)
    d = a - b * c
    return Question(
        unit=2, section="fill_blank", difficulty=diff,
        content=f"计算 {a} − {b} × {c} 时，先算（   ）法，再算（   ）法，结果是（   ）。",
        answer=f"乘；减；{d}",
        knowledge_point="运算顺序", tags="填空,顺序",
        source="generated",
    )


def _gen_fb_reading(diff: int) -> Question:
    """万以内数读写"""
    templates = [
        (f"{_rand(2,9)}000", "几千"),
        (_rand(1000, 9999), "任意四位数"),
    ]
    num = templates[0][0] if diff <= 2 else str(templates[1][0])
    # 数字转中文
    digit_map = "零一二三四五六七八九"
    unit_map = ["", "十", "百", "千"]
    parts = []
    n = int(num)
    for i in range(3, -1, -1):
        d = (n // (10 ** i)) % 10
        if d > 0:
            parts.append(digit_map[d] + unit_map[i])
        elif parts and parts[-1] != "零":
            parts.append("零")
    reading = "".join(parts).rstrip("零")
    if reading.endswith("零"):
        reading = reading[:-1]

    return Question(
        unit=3, section="fill_blank", difficulty=diff,
        content=f"{num} 读作（                      ）。",
        answer=reading,
        knowledge_point="万以内数读法", tags="填空,读数",
        source="generated",
    )


def _gen_fb_compare(diff: int) -> Question:
    """数的大小比较"""
    a = _rand(1000, 9999)
    b = _rand(1000, 9999)
    while b == a:
        b = _rand(1000, 9999)
    return Question(
        unit=3, section="fill_blank", difficulty=diff,
        content=f"在 {a} 和 {b} 中，最大的数是（      ），最小的数是（      ）。",
        answer=f"{max(a,b)}；{min(a,b)}",
        knowledge_point="数的大小比较", tags="填空,比较",
        source="generated",
    )


def _gen_fb_unit_conv(diff: int) -> Question:
    """长度单位换算填空"""
    return _gen_oral_length(diff)


def _gen_fb_length_select(diff: int) -> Question:
    """选择合适的长度单位"""
    items = [
        ("课桌高约 7（    ）", "dm"),
        ("大象高约 3（    ）", "m"),
        ("橡皮厚约 8（    ）", "mm"),
        ("铅笔长约 18（    ）", "cm"),
        ("操场跑道长 400（    ）", "m"),
        ("硬币厚约 1（    ）", "mm"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=4, section="fill_blank", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="长度单位选择", tags="填空,单位",
        source="generated",
    )


def _gen_fb_angle(diff: int) -> Question:
    """角的认识"""
    templates = [
        ("角有一个（    ）和两条（    ）。", "顶点；边"),
        ("比直角小的角叫（    ）角，比直角大的角叫（    ）角。", "锐；钝"),
        ("长方形四个角都是（    ）角。", "直"),
    ]
    content, answer = random.choice(templates)
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="角的认识", tags="填空,图形",
        source="generated",
    )


def _gen_fb_clock_walk(diff: int) -> Question:
    """钟面指针走动"""
    start = _rand(1, 10)
    end = _rand(start + 1, 12)
    minutes = (end - start) * 5
    return Question(
        unit=7, section="fill_blank", difficulty=diff,
        content=f"分针从 {start} 走到 {end}，走了（    ）分。",
        answer=str(minutes),
        knowledge_point="钟面走动", tags="填空,时钟",
        source="generated",
    )


def _gen_fb_elapsed_time(diff: int) -> Question:
    """经过时间计算"""
    h = _rand(7, 8)
    m1 = _rand(0, 3) * 10
    m2 = _rand(4, 5) * 10 + _rand(0, 9)
    total_min = (h * 60 + m2) - (h * 60 + m1)
    return Question(
        unit=7, section="fill_blank", difficulty=max(diff, 2),
        content=f"小明 {h}:{m1:02d} 从家出发，{h}:{m2:02d} 到校，路上用了（    ）分。",
        answer=str(total_min),
        knowledge_point="经过时间", tags="填空,时间",
        source="generated",
    )


def _gen_gfx_count_angles(diff: int) -> Question:
    """图形题：数角"""
    shapes = [
        ("△", "三角形", 3),
        ("□", "正方形", 4),
        ("▭", "长方形", 4),
        ("⬠", "五边形", 5),
        ("⬡", "六边形", 6),
        ("▱", "平行四边形", 4),
    ]
    selected = random.sample(shapes, min(4, len(shapes)))
    graphic = {
        "type": "count_angles",
        "shapes": [{"symbol": s[0], "label": s[1]} for s in selected],
    }
    answers = "；".join(str(s[2]) for s in selected)
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content="下面各有几个角？填在括号里。",
        answer=answers,
        knowledge_point="数角", tags=f"图形,数角,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_gfx_angle_identify(diff: int) -> Question:
    """图形题：角分类"""
    angle_data = [
        ("╲", "钝角"), ("∠", "锐角"), ("┌", "直角"),
    ]
    random.shuffle(angle_data)
    # 用序号作为 label，不泄露答案；答案单独存储在 answer 字段
    graphic = {
        "type": "angle_identify",
        "angles": [
            {"symbol": a[0], "label": f"第{i+1}个"}
            for i, a in enumerate(angle_data)
        ],
    }
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content="用三角尺比一比，下面的角各是什么角？",
        answer="；".join(a[1] for a in angle_data),
        knowledge_point="角的分类", tags=f"图形,角识别,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_gfx_grid_count(diff: int) -> Question:
    """图形题：数长方形"""
    rows = random.choice([2, 2, 3])
    cols = random.choice([2, 3, 3])
    # 计算网格中的长方形总数
    total_rects = rows * (rows + 1) // 2 * cols * (cols + 1) // 2
    graphic = {"type": "grid_count", "rows": rows, "cols": cols}
    return Question(
        unit=6, section="fill_blank", difficulty=min(diff + 1, 4),
        content=f"数一数，下图中有几个长方形？",
        answer=str(total_rects),
        knowledge_point="数长方形",
        tags=f"图形,数长方形,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_clock_read(diff: int) -> Question:
    """图形题：钟面读时"""
    h = _rand(1, 12)
    m = _rand(0, 11) * 5  # 0,5,10,...,55
    # 格式化为时间
    answer = f"{h}:{m:02d}"
    graphic = {"type": "clock", "clocks": [{"hour": h, "minute": m}]}
    return Question(
        unit=7, section="fill_blank", difficulty=diff,
        content="写出下面钟面上的时间。",
        answer=answer,
        knowledge_point="读钟面",
        tags=f"图形,钟面,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_clock_elapsed(diff: int) -> Question:
    """图形题：经过时间"""
    h = _rand(7, 10)
    m1 = _rand(0, 3) * 15
    m2 = m1 + _rand(1, 4) * 15
    m3 = m2 + _rand(1, 3) * 15
    t1 = f"{h}:{m1:02d}"
    t2 = f"{h}:{m2:02d}"
    t3 = f"{h}:{m3:02d}" if m3 < 60 else f"{h+1}:{(m3-60):02d}"
    graphic = {
        "type": "clock",
        "clocks": [
            {"hour": h, "minute": m1},
            {"hour": h, "minute": m2},
            {"hour": h + 1 if m3 >= 60 else h, "minute": m3 % 60},
        ]
    }
    d1 = m2 - m1
    d2 = m3 - m2 if m3 < 60 else (m3 - 60) + (60 - m2)
    return Question(
        unit=7, section="fill_blank", difficulty=diff,
        content="写出钟面上的时间并计算经过时间。",
        answer=f"{t1} -> {t2} -> {t3}; 经过{d1}分; 经过{d2}分",
        knowledge_point="经过时间",
        tags=f"图形,钟面,经过时间,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_cube_stack(diff: int) -> Question:
    """图形题：立方体堆叠计数"""
    if diff <= 2:
        rows, cols = 2, 2
    else:
        rows, cols = random.choice([(2, 3), (3, 2), (3, 3)])

    grid = []
    total = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            max_h = rows - r  # 后排可以更高
            h = _rand(0, min(max_h, 3))
            row.append(h)
            total += h
        grid.append(row)

    graphic = {"type": "cube_stack", "grid": grid}
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content="数一数，下面的图形由几个小立方体搭成？",
        answer=str(total),
        knowledge_point="数立方体",
        tags=f"图形,立方体,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_cube_view(diff: int) -> Question:
    """图形题：三视图立方体"""
    cols = _rand(2, 3)
    front = [_rand(1, 3) for _ in range(cols)]
    side = [_rand(1, min(3, max(front))) for _ in range(_rand(2, 3))]
    graphic = {"type": "cube_view", "front": front, "side": side}
    answer = sum(front) + sum(side)  # 简化估算
    return Question(
        unit=6, section="fill_blank", difficulty=min(diff + 1, 5),
        content="根据从正面和侧面看到的形状，算一算一共有几个小立方体？",
        answer=str(answer),
        knowledge_point="三视图",
        tags=f"图形,立方体,三视图,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_gfx_shape_classify(diff: int) -> Question:
    """图形题：图形分类/命名"""
    shape_pool = [
        ("△", "三角形"), ("□", "正方形"), ("▭", "长方形"),
        ("▱", "平行四边形"), ("○", "圆"), ("⬠", "五边形"),
        ("⬡", "六边形"),
    ]
    selected = random.sample(shape_pool, min(4, len(shape_pool)))
    # label 留空，让渲染器使用通用标识（"图形1"等），避免泄露答案
    graphic = {
        "type": "shape_classify",
        "shapes": [{"symbol": s[0], "label": ""} for s in selected],
    }
    answers = "；".join(s[1] for s in selected)
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content="写出下面图形的名称。",
        answer=answers,
        knowledge_point="图形识别",
        tags=f"图形,图形分类,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


def _gen_gfx_parallelogram(diff: int) -> Question:
    """图形题：平行四边形变形"""
    contents = [
        "看一看，长方形拉成平行四边形后，什么变了？什么没变？",
        "用手拉一拉长方形木框，变成了什么图形？这个图形的对边还相等吗？",
    ]
    answers = [
        "形状变了（角变了），边长没变",
        "平行四边形；对边仍然相等",
    ]
    idx = diff - 2  # diff 2->0, diff 3->1
    idx = max(0, min(idx, len(contents) - 1))
    graphic = {"type": "parallelogram"}
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content=contents[idx],
        answer=answers[idx],
        knowledge_point="平行四边形特性",
        tags=f"图形,平行四边形,变形,graphic:{json.dumps(graphic, ensure_ascii=False)}",
        source="generated",
    )


FILL_BLANK_GENERATORS = [
    (_gen_fb_remainder_relation, 2),
    (_gen_fb_find_dividend, 2),
    (_gen_fb_find_dividend, 3),
    (_gen_fb_mix_order, 2),
    (_gen_fb_mix_order, 3),
    (_gen_fb_reading, 1),
    (_gen_fb_reading, 2),
    (_gen_fb_compare, 2),
    (_gen_fb_unit_conv, 1),
    (_gen_fb_unit_conv, 2),
    (_gen_fb_length_select, 2),
    (_gen_fb_length_select, 3),
    (_gen_fb_angle, 1),
    (_gen_fb_angle, 2),
    (_gen_fb_clock_walk, 2),
    (_gen_fb_elapsed_time, 2),
    (_gen_fb_elapsed_time, 3),
    # 图形题生成器
    (_gen_gfx_count_angles, 2),
    (_gen_gfx_count_angles, 3),
    (_gen_gfx_angle_identify, 1),
    (_gen_gfx_angle_identify, 2),
    (_gen_gfx_grid_count, 2),
    (_gen_gfx_grid_count, 3),
    # 钟面生成器
    (_gen_clock_read, 1),
    (_gen_clock_read, 2),
    (_gen_clock_elapsed, 2),
    (_gen_clock_elapsed, 3),
    # 立方体生成器
    (_gen_cube_stack, 2),
    (_gen_cube_stack, 3),
    (_gen_cube_view, 3),
    # 图形分类 & 变形生成器
    (_gen_gfx_shape_classify, 1),
    (_gen_gfx_shape_classify, 2),
    (_gen_gfx_parallelogram, 2),
    (_gen_gfx_parallelogram, 3),
]


# ============================================================
# 三、选择题生成 (choice)
# ============================================================

def _gen_ch_round_up(diff: int) -> Question:
    """进一法选择题"""
    total = _rand(20, 50)
    per = _rand(4, 8)
    q, r = divmod(total, per)
    need = q + (1 if r > 0 else 0)
    wrongs = [q, q + 2, total]
    options = [need] + random.sample([w for w in wrongs if w != need], 3)
    random.shuffle(options)
    letters = "ABCD"
    correct_letter = letters[options.index(need)]
    return Question(
        unit=1, section="choice", difficulty=diff,
        content=f"有 {total} 个苹果，每盘放 {per} 个，至少需要（    ）个盘子。",
        answer=correct_letter,
        options=json.dumps([f"{letters[i]}. {v}" for i, v in enumerate(options)], ensure_ascii=False),
        knowledge_point="进一法", tags="选择,应用",
        source="generated",
    )


def _gen_ch_remainder_max(diff: int) -> Question:
    """余数范围判断"""
    correct = _rand(4, 8)
    correct_max = correct - 1
    distractors = [correct_max - 2, correct_max + 1, correct_max + 2]
    distractors = [d for d in distractors if d != correct_max and d >= 0][:3]
    options = [correct_max] + distractors[:3]
    random.shuffle(options)
    letters = "ABCD"
    correct_letter = letters[options.index(correct_max)]
    return Question(
        unit=1, section="choice", difficulty=diff,
        content=f"一个数除以 {correct}，余数最大是（    ）。",
        answer=correct_letter,
        options=json.dumps([f"{letters[i]}. {v}" for i, v in enumerate(options)], ensure_ascii=False),
        knowledge_point="余数范围", tags="选择,余数",
        source="generated",
    )


def _gen_ch_angle_size(diff: int) -> Question:
    """角的大小与什么有关"""
    return Question(
        unit=6, section="choice", difficulty=diff,
        content="角的大小与（    ）有关。",
        answer="B",
        options=json.dumps(
            ["A. 边的长短", "B. 张口的大小", "C. 顶点的位置", "D. 以上都是"],
            ensure_ascii=False,
        ),
        knowledge_point="角的大小", tags="选择,图形",
        source="generated",
    )


def _gen_ch_time_diff(diff: int) -> Question:
    """时间快慢比较"""
    names = ["小红", "小英", "小云"]
    times = [_rand(10, 20) for _ in range(3)]
    # 确保不重复
    while len(set(times)) < 3:
        times = [_rand(10, 20) for _ in range(3)]
    fastest = names[times.index(min(times))]
    options = names[:]
    random.shuffle(options)
    letters = "ABCD"
    correct_letter = letters[options.index(fastest)]
    return Question(
        unit=7, section="choice", difficulty=diff,
        content=f"跑 60 米，{names[0]} {times[0]} 秒，{names[1]} {times[1]} 秒，{names[2]} {times[2]} 秒，谁跑得最快？（    ）",
        answer=correct_letter,
        options=json.dumps([f"{letters[i]}. {v}" for i, v in enumerate(options)], ensure_ascii=False),
        knowledge_point="时间比较", tags="选择,快慢",
        source="generated",
    )


CHOICE_GENERATORS = [
    (_gen_ch_round_up, 3),
    (_gen_ch_remainder_max, 2),
    (_gen_ch_remainder_max, 3),
    (_gen_ch_angle_size, 2),
    (_gen_ch_angle_size, 3),
    (_gen_ch_time_diff, 3),
]


# ============================================================
# 四、竖式计算生成 (vertical_calc)
# ============================================================

def _gen_vc_div_vertical(diff: int) -> Question:
    """除法竖式"""
    d = _rand(3, 8)
    q = _rand(3, 12)
    r = _rand(1, d - 1) if diff >= 3 else 0
    dividend = d * q + r
    answer = f"{q}...{r}" if r > 0 else str(q)
    return Question(
        unit=1, section="vertical_calc", difficulty=diff,
        content=f"用竖式计算：{dividend} ÷ {d} =",
        answer=answer,
        knowledge_point="除法竖式", tags="竖式,除法",
        source="generated",
    )


def _gen_vc_mix_detach(diff: int) -> Question:
    """脱式计算"""
    a = _rand(20, 80)
    b = _rand(3, 9)
    c = _rand(3, 9)

    if diff <= 3:
        # 两步：乘加、除减等
        patterns = [
            (f"{a} + {b} × {c}", a + b * c),
            (f"{a} - {b} × {c}", a - b * c),
            (f"{b * c} ÷ {c} + {a}", b + a),
        ]
    else:
        # 三步带括号
        patterns = [
            (f"({a} - {b * c}) × {c}", (a - b * c) * c),
            (f"({a} + {b * c}) ÷ {c}", (a + b * c) // c if (a + b * c) % c == 0 else None),
        ]
        patterns = [(e, r) for e, r in patterns if r is not None]

    expr, result = random.choice(patterns)
    return Question(
        unit=2, section="vertical_calc", difficulty=diff,
        content=f"脱式计算：{expr}",
        answer=str(result),
        knowledge_point="脱式计算", tags="脱式,混合",
        source="generated",
    )


def _gen_vc_3digit_vertical(diff: int) -> Question:
    """三位数加减竖式"""
    a = _rand(200, 999)
    b = _rand(100, 999)

    if diff <= 3:
        op = random.choice(["+", "-"])
        if op == "+":
            result = a + b
            expr = f"{a} + {b}"
        else:
            if a < b:
                a, b = b, a
            result = a - b
            expr = f"{a} - {b}"
    else:
        # 减法是退位的
        a = _rand(300, 999)
        b = _rand(100, a)
        # 确保有退位
        while (a % 10) >= (b % 10) and (a // 10 % 10) >= (b // 10 % 10):
            b = _rand(100, a)
        result = a - b
        expr = f"{a} - {b}"

    return Question(
        unit=5, section="vertical_calc", difficulty=diff,
        content=f"用竖式计算：{expr} =",
        answer=str(result),
        knowledge_point="三位数加减竖式", tags="竖式,加减",
        source="generated",
    )


VERTICAL_GENERATORS = [
    (_gen_vc_div_vertical, 2),
    (_gen_vc_div_vertical, 3),
    (_gen_vc_div_vertical, 4),
    (_gen_vc_mix_detach, 2),
    (_gen_vc_mix_detach, 3),
    (_gen_vc_mix_detach, 4),
    (_gen_vc_3digit_vertical, 2),
    (_gen_vc_3digit_vertical, 3),
    (_gen_vc_3digit_vertical, 4),
    (_gen_vc_3digit_vertical, 5),
]


# ============================================================
# 五、应用题生成 (word_problem) — 模板法
# ============================================================

WORD_PROBLEM_TEMPLATES = [
    # (unit, difficulty, template_func_name引用的dict)
    {
        "unit": 1, "difficulty": 3, "kp": "进一法",
        "content": "二(1)班有 {total} 名同学去划船，每条船最多坐 {per} 人。他们至少需要租几条船？",
        "answer": "{total}÷{per}={q}(条)……{r}(人), {q}+1={need}(条)",
        "gen_params": lambda: _round_up_params(),
        "tags": "应用,进一法",
    },
    {
        "unit": 1, "difficulty": 3, "kp": "去尾法",
        "content": "妈妈买了 {total} 颗扣子，每件衣服需要钉 {per} 颗扣子。最多可以钉几件衣服？",
        "answer": "{total}÷{per}={q}(件)……{r}(颗), 最多钉{q}件",
        "gen_params": lambda: _round_down_params(),
        "tags": "应用,去尾法",
    },
    {
        "unit": 1, "difficulty": 4, "kp": "有余数综合",
        "content": "有 {total} 个气球，每 {per} 个扎成一束。最多可以扎几束？至少再加几个气球才能再扎一束？",
        "answer": "{total}÷{per}={q}(束)……{r}(个)；{per}-{r}={need}(个)",
        "gen_params": lambda: _balloon_params(),
        "tags": "应用,综合",
    },
    {
        "unit": 2, "difficulty": 3, "kp": "乘加两步",
        "content": "面包每个 {bread} 元，饮料每瓶 {drink} 元。买 {n} 个面包和 1 瓶饮料，应付多少元？",
        "answer": "{bread}×{n}={sub}(元), {sub}+{drink}={total}(元)",
        "gen_params": lambda: _shop_params(),
        "tags": "应用,购物",
    },
    {
        "unit": 2, "difficulty": 4, "kp": "多步购物",
        "content": "小明带了 {money} 元，买了 {n} 个笔记本（每个 {price} 元），还剩多少元？",
        "answer": "{n}×{price}={spent}(元), {money}-{spent}={remain}(元)",
        "gen_params": lambda: _notebook_params(),
        "tags": "应用,多步",
    },
    {
        "unit": 4, "difficulty": 3, "kp": "长度应用",
        "content": "小明家离学校 {dist} m，他走了 {walked} m，还要走多少米到学校？",
        "answer": "{dist}-{walked}={remain}(m)",
        "gen_params": lambda: _length_params(),
        "tags": "应用,长度",
    },
    {
        "unit": 5, "difficulty": 4, "kp": "多步加减",
        "content": "图书馆有故事书 {story} 本，科技书比故事书少 {less} 本。两种书一共有多少本？",
        "answer": "{story}-{less}={tech}(本), {story}+{tech}={total}(本)",
        "gen_params": lambda: _library_params(),
        "tags": "应用,比多比少",
    },
    {
        "unit": 5, "difficulty": 4, "kp": "加减混合",
        "content": "超市原有苹果 {orig} 千克，上午卖出 {sold} 千克，下午又运进 {new} 千克。现在有多少千克苹果？",
        "answer": "{orig}-{sold}={after_sold}(kg), {after_sold}+{new}={now}(kg)",
        "gen_params": lambda: _store_params(),
        "tags": "应用,混合",
    },
    {
        "unit": 7, "difficulty": 3, "kp": "结束时间",
        "content": "小明 {hour}:{minute:02d} 从家出发去学校，走到学校用了 {walk} 分钟。小明几时几分到校？",
        "answer": "{hour}:{minute:02d}+{walk}分={arr_h}:{arr_m:02d}",
        "gen_params": lambda: _time_arrive_params(),
        "tags": "应用,时间",
    },
    {
        "unit": 7, "difficulty": 4, "kp": "经过时间",
        "content": "电影 {h1}:{m1:02d} 开始，{h2}:{m2:02d} 结束。电影放映了多长时间？",
        "answer": "{h2}:{m2:02d}-{h1}:{m1:02d}={diff_h}时{diff_m}分",
        "gen_params": lambda: _movie_params(),
        "tags": "应用,时间",
    },
]


def _round_up_params():
    total = _rand(15, 50)
    per = _rand(4, 8)
    q, r = divmod(total, per)
    need = q + 1
    return {"total": total, "per": per, "q": q, "r": r, "need": need}


def _round_down_params():
    total = _rand(30, 80)
    per = _rand(6, 10)
    q, r = divmod(total, per)
    return {"total": total, "per": per, "q": q, "r": r}


def _balloon_params():
    total = _rand(15, 40)
    per = _rand(5, 8)
    q, r = divmod(total, per)
    need = per - r
    return {"total": total, "per": per, "q": q, "r": r, "need": need}


def _shop_params():
    bread = _rand(2, 5)
    drink = _rand(4, 8)
    n = _rand(3, 6)
    return {
        "bread": bread, "drink": drink, "n": n,
        "sub": bread * n, "total": bread * n + drink,
    }


def _notebook_params():
    money = _rand(20, 50)
    n = _rand(3, 6)
    price = _rand(3, 6)
    spent = n * price
    return {
        "money": money, "n": n, "price": price,
        "spent": spent, "remain": money - spent,
    }


def _length_params():
    dist = _rand(500, 1500) // 100 * 100
    walked = _rand(200, 700) // 100 * 100
    return {
        "dist": dist, "walked": walked,
        "remain": dist - walked,
    }


def _library_params():
    story = _rand(200, 500)
    less = _rand(50, 150)
    tech = story - less
    return {
        "story": story, "less": less,
        "tech": tech, "total": story + tech,
    }


def _store_params():
    orig = _rand(300, 600)
    sold = _rand(100, 250)
    new = _rand(100, 300)
    after_sold = orig - sold
    return {
        "orig": orig, "sold": sold, "new": new,
        "after_sold": after_sold, "now": after_sold + new,
    }


def _time_arrive_params():
    hour = _rand(7, 8)
    minute = 0 if random.random() > 0.5 else 30
    walk = _rand(15, 35)
    total_min = minute + walk
    arr_h = hour + total_min // 60
    arr_m = total_min % 60
    return {"hour": hour, "minute": minute, "walk": walk,
            "arr_h": arr_h, "arr_m": arr_m}


def _movie_params():
    h1, m1 = 9, _rand(0, 3) * 15
    h2 = h1 + _rand(1, 2)
    m2 = _rand(1, 5) * 10 + _rand(0, 9)
    t1 = h1 * 60 + m1
    t2 = h2 * 60 + m2
    diff = t2 - t1
    return {"h1": h1, "m1": m1, "h2": h2, "m2": m2,
            "diff_h": diff // 60, "diff_m": diff % 60}


def _gen_word_problem() -> Question:
    """从模板生成应用题（每个模板自包含所有计算值）"""
    tmpl = random.choice(WORD_PROBLEM_TEMPLATES)
    params = tmpl["gen_params"]()
    content = tmpl["content"].format(**params)
    answer = tmpl["answer"].format(**params)
    return Question(
        unit=tmpl["unit"], section="word_problem", difficulty=tmpl["difficulty"],
        content=content, answer=answer,
        knowledge_point=tmpl["kp"], tags=tmpl.get("tags", ""),
        source="generated",
    )


# ============================================================
# 批量生成入口
# ============================================================

def generate_questions(
    count: int = 30,
    sections: list = None,
    units: list = None,
) -> List[Question]:
    """
    批量生成题目。

    参数：
        count: 生成数量（约数，实际可能略少）
        sections: 限定题型，None=全部
        units: 限定单元，None=全部
    """
    if sections is None:
        sections = ["oral_calc", "fill_blank", "choice", "vertical_calc", "word_problem"]

    all_generators = []
    if "oral_calc" in sections:
        all_generators.extend(ORAL_GENERATORS)
    if "fill_blank" in sections:
        all_generators.extend(FILL_BLANK_GENERATORS)
    if "choice" in sections:
        all_generators.extend(CHOICE_GENERATORS)
    if "vertical_calc" in sections:
        all_generators.extend(VERTICAL_GENERATORS)
    if "word_problem" in sections:
        # 应用题用模板，重复生成时有变体
        pass

    questions = []
    attempts = 0
    max_attempts = count * 3

    while len(questions) < count and attempts < max_attempts:
        attempts += 1

        if "word_problem" in sections and random.random() < 0.15:
            q = _gen_word_problem()
        elif all_generators:
            gen_fn, diff = random.choice(all_generators)
            try:
                q = gen_fn(diff)
            except Exception:
                continue
        else:
            q = _gen_word_problem()

        # 单元过滤
        if units and q.unit not in units:
            continue

        questions.append(q)

    return questions
