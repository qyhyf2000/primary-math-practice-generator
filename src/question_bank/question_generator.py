"""
算法题目生成器 — 自动生成小学数学题，支持1-6年级上下册

GradeProfile 定义各年级数值边界和运算能力，生成器通过注册表按能力筛选。
"""
import random
import json
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from .models import Question


# ============================================================
# 年级知识画像
# ============================================================

@dataclass
class GradeProfile:
    """年级知识边界——控制生成器出题范围和类型"""
    grade: int
    term: int
    label: str = ""

    # 数值范围
    max_number: int = 100
    max_digits: int = 3              # 最大位数
    supports_negative: bool = False

    # 运算能力
    supports_multiplication: bool = False
    supports_division: bool = False
    supports_remainder: bool = False
    times_table_max: int = 0         # 乘法口诀最大数（0=不支持）
    supports_fractions: bool = False
    supports_decimals: bool = False

    # 几何范围
    geometry_angles: bool = False     # 角的识别
    geometry_shapes: bool = False     # 长方形/正方形/平行四边形
    geometry_cubes: bool = False      # 立方体/三视图
    geometry_tangram: bool = False    # 七巧板

    # 测量
    length_units: tuple = ()
    time_units: tuple = ("时", "分")


# 12个学期的知识画像
PROFILES: dict = {
    "1-1": GradeProfile(grade=1, term=1, label="一年级上册",
                         max_number=20, max_digits=1),
    "1-2": GradeProfile(grade=1, term=2, label="一年级下册",
                         max_number=100, max_digits=2,
                         geometry_shapes=True),
    "2-1": GradeProfile(grade=2, term=1, label="二年级上册",
                         max_number=100, max_digits=2,
                         supports_multiplication=True, supports_division=True,
                         times_table_max=9,
                         geometry_shapes=True,
                         length_units=("m", "cm")),
    "2-2": GradeProfile(grade=2, term=2, label="二年级下册",
                         max_number=10000, max_digits=4,
                         supports_multiplication=True, supports_division=True,
                         supports_remainder=True, times_table_max=9,
                         geometry_angles=True, geometry_shapes=True,
                         geometry_cubes=True, geometry_tangram=True,
                         length_units=("km", "m", "dm", "cm", "mm"),
                         time_units=("时", "分", "秒")),
    "3-1": GradeProfile(grade=3, term=1, label="三年级上册",
                         max_number=10000, max_digits=4,
                         supports_multiplication=True, supports_division=True,
                         supports_decimals=True, times_table_max=9,
                         geometry_angles=True, geometry_shapes=True,
                         length_units=("km", "m", "dm", "cm", "mm")),
    "3-2": GradeProfile(grade=3, term=2, label="三年级下册",
                         max_number=100000, max_digits=5,
                         supports_multiplication=True, supports_division=True,
                         supports_fractions=True, supports_decimals=True,
                         geometry_shapes=True, geometry_cubes=True),
    "4-1": GradeProfile(grade=4, term=1, label="四年级上册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_negative=True,
                         geometry_angles=True, geometry_shapes=True,
                         length_units=("km", "m", "dm", "cm", "mm")),
    "4-2": GradeProfile(grade=4, term=2, label="四年级下册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_decimals=True,
                         geometry_shapes=True, geometry_cubes=True),
    "5-1": GradeProfile(grade=5, term=1, label="五年级上册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_fractions=True, supports_decimals=True,
                         geometry_shapes=True),
    "5-2": GradeProfile(grade=5, term=2, label="五年级下册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_fractions=True, supports_decimals=True,
                         geometry_shapes=True, geometry_cubes=True),
    "6-1": GradeProfile(grade=6, term=1, label="六年级上册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_fractions=True, supports_decimals=True,
                         supports_negative=True,
                         geometry_shapes=True),
    "6-2": GradeProfile(grade=6, term=2, label="六年级下册",
                         max_number=100000000, max_digits=9,
                         supports_multiplication=True, supports_division=True,
                         supports_fractions=True, supports_decimals=True,
                         supports_negative=True,
                         geometry_shapes=True, geometry_cubes=True),
}


def _rand(a, b):
    return random.randint(a, b)


def get_profile(grade: int = 2, term: int = 2) -> GradeProfile:
    """获取指定年级/学期的知识画像"""
    key = f"{grade}-{term}"
    return PROFILES.get(key, PROFILES["2-2"])


# ============================================================
# 一、口算题生成 (oral_calc)
# ============================================================

def _gen_oral_div_table(diff: int = 1) -> Question:
    """表内除法口算"""
    b = _rand(2, 9)
    c = _rand(2, 9)
    a = b * c
    return Question(
        unit=1, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} =",
        answer=str(c),
        knowledge_point="表内除法", tags="口算,除法",
        source="generated",
    )


def _gen_oral_div_remainder(diff: int = 1) -> Question:
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


def _gen_oral_mix_mult_add(diff: int = 1) -> Question:
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


def _gen_oral_mix_div_sub(diff: int = 1) -> Question:
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


def _gen_oral_mix_paren(diff: int = 1) -> Question:
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


def _gen_oral_length(diff: int = 1) -> Question:
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


def _gen_oral_3digit_add(diff: int = 1) -> Question:
    """三位数加法口算"""
    a = _rand(100, 999)
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


def _gen_oral_3digit_sub(diff: int = 1) -> Question:
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


def _gen_oral_time(diff: int = 1) -> Question:
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


# ============================================================
# 一年级专属生成器
# ============================================================

def _gen_oral_add_1digit(diff: int = 1) -> Question:
    """10以内加法"""
    a = _rand(1, 9)
    b = _rand(1, 10 - a)
    return Question(
        unit=_rand(1, 3), section="oral_calc", difficulty=diff,
        content=f"{a} + {b} =",
        answer=str(a + b),
        knowledge_point="10以内加法", tags="口算,加法",
        source="generated",
    )


def _gen_oral_sub_1digit(diff: int = 1) -> Question:
    """10以内减法"""
    a = _rand(3, 10)
    b = _rand(1, a)
    return Question(
        unit=_rand(1, 3), section="oral_calc", difficulty=diff,
        content=f"{a} - {b} =",
        answer=str(a - b),
        knowledge_point="10以内减法", tags="口算,减法",
        source="generated",
    )


def _gen_oral_add_carry(diff: int = 1) -> Question:
    """20以内进位加法（凑十法）"""
    a = _rand(7, 9)
    b = _rand(3, 9)
    return Question(
        unit=7, section="oral_calc", difficulty=min(diff + 1, 3),
        content=f"{a} + {b} =",
        answer=str(a + b),
        knowledge_point="20以内进位加法", tags="口算,进位",
        source="generated",
    )


def _gen_oral_sub_borrow(diff: int = 1) -> Question:
    """20以内退位减法（破十法）"""
    a = _rand(11, 18)
    b = _rand(2, 9)
    if a - b < 0:
        a, b = b + _rand(1, 5), _rand(1, 5)
    return Question(
        unit=7, section="oral_calc", difficulty=min(diff + 1, 3),
        content=f"{a} - {b} =",
        answer=str(a - b),
        knowledge_point="20以内退位减法", tags="口算,退位",
        source="generated",
    )


def _gen_oral_2digit_add_1digit(diff: int = 1) -> Question:
    """两位数加一位数（不进位）"""
    a = _rand(10, 80)
    b = _rand(1, min(9, 99 - a))
    return Question(
        unit=5, section="oral_calc", difficulty=diff,
        content=f"{a} + {b} =",
        answer=str(a + b),
        knowledge_point="两位数加一位数", tags="口算,加法",
        source="generated",
    )


def _gen_oral_2digit_sub_1digit(diff: int = 1) -> Question:
    """两位数减一位数"""
    a = _rand(11, 99)
    b = _rand(1, min(9, a - 1))
    return Question(
        unit=5, section="oral_calc", difficulty=diff,
        content=f"{a} - {b} =",
        answer=str(a - b),
        knowledge_point="两位数减一位数", tags="口算,减法",
        source="generated",
    )


def _gen_oral_round_add(diff: int = 1) -> Question:
    """整十数加减"""
    a = _rand(1, 9) * 10
    b = _rand(1, 9) * 10
    if _rand(0, 1):
        content, answer = f"{a} + {b} =", str(a + b)
        kp = "整十数加法"
    else:
        if a < b:
            a, b = b, a
        content, answer = f"{a} - {b} =", str(a - b)
        kp = "整十数减法"
    return Question(
        unit=5, section="oral_calc", difficulty=diff,
        content=content, answer=answer,
        knowledge_point=kp, tags="口算,整十数",
        source="generated",
    )


# -- 一年级填空生成器 --

def _gen_fb_num_sequence(diff: int = 1) -> Question:
    """按规律填数"""
    start = _rand(1, 20)
    step = _rand(1, 3)
    seq = [start + step * i for i in range(5)]
    blank_idx = _rand(1, 3)
    answer = str(seq[blank_idx])
    seq[blank_idx] = "（  ）"
    return Question(
        unit=_rand(1, 4), section="fill_blank", difficulty=diff,
        content="、".join(str(x) for x in seq),
        answer=answer,
        knowledge_point="数的顺序", tags="填空,规律",
        source="generated",
    )


def _gen_fb_compare_num(diff: int = 1) -> Question:
    """比较数的大小（填入 > < =）"""
    a = _rand(1, 99)
    b = _rand(1, 99)
    cmp = ">" if a > b else ("<" if a < b else "=")
    return Question(
        unit=_rand(1, 4), section="fill_blank", difficulty=diff,
        content=f"{a} ○ {b}",
        answer=cmp,
        knowledge_point="比较大小", tags="填空,比较",
        source="generated",
    )


def _gen_fb_number_name(diff: int = 1) -> Question:
    """数的读写"""
    nums = [
        (15, "十五"), (23, "二十三"), (38, "三十八"),
        (50, "五十"), (67, "六十七"), (84, "八十四"),
        (91, "九十一"), (100, "一百"),
    ]
    n, name = random.choice(nums)
    if _rand(0, 1):
        return Question(
            unit=4, section="fill_blank", difficulty=diff,
            content=f"{n} 读作（    ）",
            answer=name,
            knowledge_point="数的读写", tags="填空,读数",
            source="generated",
        )
    else:
        return Question(
            unit=4, section="fill_blank", difficulty=diff,
            content=f"{name} 写作（    ）",
            answer=str(n),
            knowledge_point="数的读写", tags="填空,写数",
            source="generated",
        )


def _gen_fb_shape_name(diff: int = 1) -> Question:
    """图形辨认填空"""
    shapes = [
        ("长方体", "立体图形"),
        ("正方体", "立体图形"),
        ("圆柱", "立体图形"),
        ("球", "立体图形"),
        ("长方形", "平面图形"),
        ("正方形", "平面图形"),
        ("三角形", "平面图形"),
        ("圆", "平面图形"),
    ]
    shape_name, category = random.choice(shapes)
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content=f"写出下面图形的名称：{shape_name}是（    ）",
        answer=shape_name,
        knowledge_point="图形辨认", tags="填空,图形",
        source="generated",
    )


def _gen_fb_position(diff: int = 1) -> Question:
    """位置关系填空"""
    items = [
        ("苹果在桌子的（    ）面", "上"),
        ("小猫在桌子的（    ）面", "下"),
        ("小明的前面是黑板，小明在教室的（    ）面", "后"),
        ("小红在小明的左边，小明在小红的（    ）边", "右"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=5, section="fill_blank", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="位置关系", tags="填空,位置",
        source="generated",
    )


def _gen_fb_clock_hour(diff: int = 1) -> Question:
    """钟表整时/半时填空"""
    hours = list(range(1, 13))
    h = random.choice(hours)
    if _rand(0, 1):
        return Question(
            unit=8, section="fill_blank", difficulty=diff,
            content=f"钟面上，时针指向{h}，分针指向12，是（    ）时。",
            answer=f"{h}时",
            knowledge_point="认识整时", tags="填空,钟表",
            source="generated",
        )
    else:
        return Question(
            unit=8, section="fill_blank", difficulty=diff,
            content=f"钟面上，时针指向{h}和{h+1 if h < 12 else 1}之间，分针指向6，是（    ）时半。",
            answer=f"{h}时半",
            knowledge_point="认识半时", tags="填空,钟表",
            source="generated",
        )


# ============================================================
# 二年级上册 + 三年级上册专属生成器
# ============================================================

# -- 二上：乘法口诀 --

def _gen_oral_mult_table(diff: int = 1) -> Question:
    """乘法口诀口算"""
    a = _rand(2, 9)
    b = _rand(1, 9)
    return Question(
        unit=_rand(3, 4), section="oral_calc", difficulty=diff,
        content=f"{a} × {b} =",
        answer=str(a * b),
        knowledge_point=f"{min(a,b)}的乘法口诀", tags="口算,乘法",
        source="generated",
    )


def _gen_oral_div_table_basic(diff: int = 1) -> Question:
    """表内除法（乘除对应）"""
    b = _rand(2, 9)
    c = _rand(1, 9)
    a = b * c
    return Question(
        unit=7, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} =",
        answer=str(c),
        knowledge_point="用乘法口诀求商", tags="口算,除法",
        source="generated",
    )


def _gen_oral_money(diff: int = 1) -> Question:
    """元角分换算"""
    items = [
        ("1 元 = ( ) 角", "10"),
        ("10 角 = ( ) 元", "1"),
        ("1 角 = ( ) 分", "10"),
        ("5 元 = ( ) 角", "50"),
        ("30 角 = ( ) 元", "3"),
        ("2 元 5 角 = ( ) 角", "25"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=2, section="oral_calc", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="元角分换算", tags="口算,购物",
        source="generated",
    )


def _gen_oral_cm_m(diff: int = 1) -> Question:
    """厘米和米换算"""
    items = [
        ("1 米 = ( ) 厘米", "100"),
        ("100 厘米 = ( ) 米", "1"),
        ("2 米 = ( ) 厘米", "200"),
        ("300 厘米 = ( ) 米", "3"),
        ("1 米 20 厘米 = ( ) 厘米", "120"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=6, section="oral_calc", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="厘米和米换算", tags="口算,测量",
        source="generated",
    )


# -- 二上填空 --

def _gen_fb_mult_meaning(diff: int = 1) -> Question:
    """乘法意义填空"""
    a = _rand(2, 5)
    b = _rand(2, 6)
    return Question(
        unit=3, section="fill_blank", difficulty=diff,
        content=f"{a} × {b} 表示（    ）个（    ）相加，也表示（    ）的（    ）倍。",
        answer=f"{b}；{a}；{a}；{b}",
        knowledge_point="乘法的意义", tags="填空,乘法",
        source="generated",
    )


def _gen_fb_money_word(diff: int = 1) -> Question:
    """购物填空"""
    price = _rand(1, 9)
    count = _rand(2, 5)
    total = price * count
    return Question(
        unit=2, section="fill_blank", difficulty=diff,
        content=f"每本练习本 {price} 角，买 {count} 本需要（    ）角，也就是（    ）元（    ）角。",
        answer=f"{total}；{total // 10}；{total % 10}",
        knowledge_point="购物计算", tags="填空,元角分",
        source="generated",
    )


# -- 三上：混合运算 + 测量 + 大数估算 --

def _gen_oral_mix_2step(diff: int = 1) -> Question:
    """两步混合运算口算"""
    a = _rand(10, 50)
    b = _rand(2, 9)
    c = _rand(2, 5)
    if _rand(0, 1):
        content = f"{a} + {b} × {c} ="
        answer = str(a + b * c)
    else:
        total = a + b * c
        content = f"{a} + ( ) × {c} = {total}"
        answer = str(b)
    return Question(
        unit=1, section="oral_calc", difficulty=min(diff + 1, 3),
        content=content, answer=answer,
        knowledge_point="混合运算", tags="口算,混合运算",
        source="generated",
    )


def _gen_oral_mm_cm_km(diff: int = 1) -> Question:
    """毫米/厘米/分米/千米换算"""
    items = [
        ("1 厘米 = ( ) 毫米", "10"),
        ("1 分米 = ( ) 厘米", "10"),
        ("1 千米 = ( ) 米", "1000"),
        ("5 厘米 = ( ) 毫米", "50"),
        ("70 毫米 = ( ) 厘米", "7"),
        ("3 千米 = ( ) 米", "3000"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=2, section="oral_calc", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="长度单位换算", tags="口算,测量",
        source="generated",
    )


def _gen_fb_estimate(diff: int = 1) -> Question:
    """估算填空（三上）"""
    a = _rand(200, 900)
    b = _rand(100, 500)
    r = round(a / 100) * 100
    s = round(b / 100) * 100
    return Question(
        unit=3, section="fill_blank", difficulty=diff,
        content=f"估算：{a} + {b} ≈ (    ) + (    ) = (    )",
        answer=f"{r}；{s}；{r + s}",
        knowledge_point="万以内加减估算", tags="填空,估算",
        source="generated",
    )


def _gen_oral_mult_1digit(diff: int = 1) -> Question:
    """多位数乘一位数口算（三上）"""
    a = _rand(10, 99)
    b = _rand(2, 9)
    return Question(
        unit=6, section="oral_calc", difficulty=min(diff + 1, 3),
        content=f"{a} × {b} =",
        answer=str(a * b),
        knowledge_point="两位数乘一位数", tags="口算,乘法",
        source="generated",
    )


# ============================================================
# 三年级下册 + 四年级专属生成器
# ============================================================

# -- 三下：两位数乘法 --

def _gen_oral_2digit_mult(diff: int = 1) -> Question:
    """两位数乘整十数口算"""
    a = _rand(10, 50)
    b = _rand(2, 9) * 10
    return Question(
        unit=1, section="oral_calc", difficulty=min(diff + 1, 3),
        content=f"{a} × {b} =",
        answer=str(a * b),
        knowledge_point="两位数乘整十数", tags="口算,乘法",
        source="generated",
    )


def _gen_oral_div_1digit(diff: int = 1) -> Question:
    """除数是一位数的除法口算"""
    b = _rand(2, 9)
    c = _rand(10, 99)
    a = b * c
    return Question(
        unit=4, section="oral_calc", difficulty=diff,
        content=f"{a} ÷ {b} =",
        answer=str(c),
        knowledge_point="除数一位数除法", tags="口算,除法",
        source="generated",
    )


def _gen_fb_perimeter(diff: int = 1) -> Question:
    """周长计算填空"""
    w = _rand(3, 15)
    h = _rand(3, 12)
    if _rand(0, 1):
        p = 2 * (w + h)
        return Question(
            unit=3, section="fill_blank", difficulty=diff,
            content=f"一个长方形长 {w} cm，宽 {h} cm，周长是（    ）cm。",
            answer=str(p),
            knowledge_point="长方形周长", tags="填空,周长",
            source="generated",
        )
    else:
        s = _rand(2, 15)
        return Question(
            unit=3, section="fill_blank", difficulty=diff,
            content=f"一个正方形边长 {s} cm，周长是（    ）cm。",
            answer=str(4 * s),
            knowledge_point="正方形周长", tags="填空,周长",
            source="generated",
        )


def _gen_fb_fraction_basic(diff: int = 1) -> Question:
    """分数初步填空"""
    den = _rand(2, 8)
    num = _rand(1, den - 1)
    return Question(
        unit=6, section="fill_blank", difficulty=diff,
        content=f"把一个西瓜平均分成 {den} 份，拿走其中的 {num} 份，拿走了（    ）/{den}。",
        answer=f"（{num}）/（{den}）",
        knowledge_point="分数的初步认识", tags="填空,分数",
        source="generated",
    )


# -- 四上：大数读写 + 角度度量 --

def _gen_fb_large_number(diff: int = 1) -> Question:
    """大数读写（四上）"""
    nums = [
        (12345678, "一千二百三十四万五千六百七十八"),
        (50060070, "五千零六万零七十"),
        (100200300, "一亿零二十万零三百"),
        (80000008, "八千万零八"),
    ]
    n, name = random.choice(nums)
    if _rand(0, 1):
        return Question(
            unit=1, section="fill_blank", difficulty=diff,
            content=f"{n} 读作（                      ）",
            answer=name,
            knowledge_point="亿以内数的读法", tags="填空,大数",
            source="generated",
        )
    else:
        return Question(
            unit=1, section="fill_blank", difficulty=diff,
            content=f"{name} 写作（          ）",
            answer=str(n),
            knowledge_point="亿以内数的写法", tags="填空,大数",
            source="generated",
        )


def _gen_fb_angle_measure(diff: int = 1) -> Question:
    """角度度量填空（四上）"""
    items = [
        ("1 周角 = ( ) 平角 = ( ) 直角", "2；4"),
        ("1 平角 = ( ) 直角", "2"),
        ("一个三角尺上最大的角是 ( ) 角，是 ( ) 度", "直；90"),
        ("比90度大的角叫 ( ) 角，比90度小的角叫 ( ) 角", "钝；锐"),
    ]
    content, answer = random.choice(items)
    return Question(
        unit=2, section="fill_blank", difficulty=diff,
        content=content, answer=answer,
        knowledge_point="角的度量", tags="填空,角度",
        source="generated",
    )


# ============================================================
# 四年级 + 五年级 + 六年级生成器
# ============================================================

# -- 四下：小数运算 --
def _gen_oral_decimal_add(diff: int = 1) -> Question:
    """小数加减口算"""
    a = round(_rand(10, 99) / 10, 1)
    b = round(_rand(10, 99) / 10, 1)
    if _rand(0, 1):
        return Question(unit=1, section="oral_calc", difficulty=diff,
            content=f"{a} + {b} =", answer=str(round(a + b, 1)),
            knowledge_point="小数加法", tags="口算,小数", source="generated")
    else:
        if a < b: a, b = b, a
        return Question(unit=1, section="oral_calc", difficulty=diff,
            content=f"{a} - {b} =", answer=str(round(a - b, 1)),
            knowledge_point="小数减法", tags="口算,小数", source="generated")


def _gen_oral_decimal_mult(diff: int = 1) -> Question:
    """小数乘法口算（五上）"""
    a = round(_rand(1, 9) / 10, 1)
    b = _rand(2, 9)
    return Question(unit=3, section="oral_calc", difficulty=min(diff + 1, 3),
        content=f"{a} × {b} =", answer=str(round(a * b, 1)),
        knowledge_point="小数乘法", tags="口算,小数", source="generated")


def _gen_fb_triangle(diff: int = 1) -> Question:
    """三角形分类填空（四下）"""
    items = [
        ("按角分类：三个角都是锐角的是（    ）三角形", "锐角"),
        ("有一个角是直角的是（    ）三角形", "直角"),
        ("有一个角是钝角的是（    ）三角形", "钝角"),
        ("三角形内角和是（    ）度", "180"),
        ("三角形任意两边之和（    ）第三边", "大于"),
    ]
    c, a = random.choice(items)
    return Question(unit=2, section="fill_blank", difficulty=diff,
        content=c, answer=a, knowledge_point="三角形分类", tags="填空,三角形",
        source="generated")


def _gen_fb_equation(diff: int = 1) -> Question:
    """简单方程填空（四下/五下）"""
    x = _rand(2, 20)
    a = _rand(1, 5)
    b = x + _rand(-3, 3)
    return Question(unit=5, section="fill_blank", difficulty=diff,
        content=f"解方程：x + {a} = {b + a}，x = (    )",
        answer=str(b), knowledge_point="解方程", tags="填空,方程",
        source="generated")


# -- 五上：多边形面积 --
def _gen_fb_polygon_area(diff: int = 1) -> Question:
    """多边形面积填空"""
    b = _rand(3, 12)
    h = _rand(2, 10)
    t = _rand(0, 2)
    if t == 0:
        return Question(unit=4, section="fill_blank", difficulty=diff,
            content=f"一个平行四边形底 {b} cm，高 {h} cm，面积是（    ）cm²。",
            answer=str(b * h), knowledge_point="平行四边形面积", tags="填空,面积",
            source="generated")
    elif t == 1:
        return Question(unit=4, section="fill_blank", difficulty=min(diff + 1, 3),
            content=f"一个三角形底 {b} cm，高 {h} cm，面积是（    ）cm²。",
            answer=str(round(b * h / 2, 1)), knowledge_point="三角形面积", tags="填空,面积",
            source="generated")
    else:
        a = _rand(3, 8)
        return Question(unit=4, section="fill_blank", difficulty=min(diff + 1, 3),
            content=f"一个梯形上底 {a} cm，下底 {b} cm，高 {h} cm，面积是（    ）cm²。",
            answer=str(round((a + b) * h / 2, 1)), knowledge_point="梯形面积", tags="填空,面积",
            source="generated")


# -- 五上：倍数因数 --
def _gen_fb_factor_multiple(diff: int = 1) -> Question:
    """倍数因数填空"""
    a = _rand(10, 50)
    return Question(unit=3, section="fill_blank", difficulty=diff,
        content=f"{a} 的因数有（                          ）。",
        answer="、".join(str(i) for i in range(1, a + 1) if a % i == 0),
        knowledge_point="找因数", tags="填空,因数", source="generated")


# -- 五下：分数运算 --
def _gen_oral_fraction_op(diff: int = 1) -> Question:
    """分数加减口算"""
    den = _rand(3, 8)
    n1 = _rand(1, den - 1)
    n2 = _rand(1, den - n1) if _rand(0, 1) else _rand(1, n1)
    op = "+" if _rand(0, 1) else "-"
    if op == "+":
        return Question(unit=1, section="oral_calc", difficulty=diff,
            content=f"{n1}/{den} + {n2}/{den} =",
            answer=f"{n1 + n2}/{den}", knowledge_point="同分母分数加法", tags="口算,分数",
            source="generated")
    else:
        a, b = max(n1, n2), min(n1, n2)
        return Question(unit=1, section="oral_calc", difficulty=diff,
            content=f"{a}/{den} - {b}/{den} =",
            answer=f"{a - b}/{den}", knowledge_point="同分母分数减法", tags="口算,分数",
            source="generated")


# -- 五下：长方体 --
def _gen_fb_cuboid(diff: int = 1) -> Question:
    """长方体表面积/体积填空"""
    l = _rand(3, 10)
    w = _rand(2, 8)
    h = _rand(2, 6)
    if _rand(0, 1):
        v = l * w * h
        return Question(unit=2, section="fill_blank", difficulty=diff,
            content=f"一个长方体长{l}cm，宽{w}cm，高{h}cm，体积是（    ）cm³。",
            answer=str(v), knowledge_point="长方体体积", tags="填空,体积",
            source="generated")
    else:
        s = 2 * (l * w + l * h + w * h)
        return Question(unit=2, section="fill_blank", difficulty=min(diff + 1, 3),
            content=f"一个长方体长{l}cm，宽{w}cm，高{h}cm，表面积是（    ）cm²。",
            answer=str(s), knowledge_point="长方体表面积", tags="填空,表面积",
            source="generated")


# -- 六上：圆 --
def _gen_fb_circle(diff: int = 1) -> Question:
    """圆周长/面积填空"""
    r = _rand(2, 10)
    if _rand(0, 1):
        pi = 3.14
        return Question(unit=1, section="fill_blank", difficulty=diff,
            content=f"一个圆的半径是 {r} cm，周长约是（    ）cm。（π取3.14）",
            answer=str(round(2 * pi * r, 2)), knowledge_point="圆的周长", tags="填空,圆",
            source="generated")
    else:
        return Question(unit=1, section="fill_blank", difficulty=min(diff + 1, 3),
            content=f"一个圆的半径是 {r} cm，面积约是（    ）cm²。（π取3.14）",
            answer=str(round(3.14 * r * r, 2)), knowledge_point="圆的面积", tags="填空,圆",
            source="generated")


# -- 六上：百分数 --
def _gen_oral_percent(diff: int = 1) -> Question:
    """百分数互化"""
    items = [
        ("0.25 = (    )%", "25"),
        ("0.5 = (    )%", "50"),
        ("0.75 = (    )%", "75"),
        ("20% = (    )（填小数）", "0.2"),
        ("1/4 = (    )%", "25"),
    ]
    c, a = random.choice(items)
    return Question(unit=4, section="oral_calc", difficulty=diff,
        content=c, answer=a, knowledge_point="百分数互化", tags="口算,百分数",
        source="generated")


# -- 六上：比 --
def _gen_fb_ratio(diff: int = 1) -> Question:
    """比的认识填空"""
    a = _rand(2, 10)
    b = _rand(2, 10)
    # simplify
    import math as _m
    g = _m.gcd(a, b)
    return Question(unit=6, section="fill_blank", difficulty=diff,
        content=f"化简比：{a} : {b} = (    ) : (    )",
        answer=f"{a//g}；{b//g}", knowledge_point="化简比", tags="填空,比",
        source="generated")


# -- 六下：圆柱 --
def _gen_fb_cylinder(diff: int = 1) -> Question:
    """圆柱体积填空"""
    r = _rand(2, 6)
    h = _rand(3, 10)
    v = round(3.14 * r * r * h, 1)
    return Question(unit=1, section="fill_blank", difficulty=min(diff + 1, 3),
        content=f"一个圆柱底面半径 {r} cm，高 {h} cm，体积约是（    ）cm³。（π取3.14）",
        answer=str(v), knowledge_point="圆柱体积", tags="填空,圆柱",
        source="generated")


# -- 六下：比例 --
def _gen_fb_proportion(diff: int = 1) -> Question:
    """比例填空"""
    a = _rand(2, 6)
    b = _rand(3, 8)
    x = a * b // _rand(2, 4)
    return Question(unit=2, section="fill_blank", difficulty=diff,
        content=f"解比例：{a} : {b} = {x} : x，x = (    )",
        answer=str(b * x // a), knowledge_point="解比例", tags="填空,比例",
        source="generated")


# -- 旧列表（已不由入口函数使用，保留兼容） --
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

def _gen_fb_remainder_relation(diff: int = 1) -> Question:
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


def _gen_fb_find_dividend(diff: int = 1) -> Question:
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


def _gen_fb_mix_order(diff: int = 1) -> Question:
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


def _gen_fb_reading(diff: int = 1) -> Question:
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


def _gen_fb_compare(diff: int = 1) -> Question:
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


def _gen_fb_unit_conv(diff: int = 1) -> Question:
    """长度单位换算填空"""
    return _gen_oral_length(diff)


def _gen_fb_length_select(diff: int = 1) -> Question:
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


def _gen_fb_angle(diff: int = 1) -> Question:
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


def _gen_fb_clock_walk(diff: int = 1) -> Question:
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


def _gen_fb_elapsed_time(diff: int = 1) -> Question:
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


def _gen_gfx_count_angles(diff: int = 1) -> Question:
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


def _gen_gfx_angle_identify(diff: int = 1) -> Question:
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


def _gen_gfx_grid_count(diff: int = 1) -> Question:
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


def _gen_clock_read(diff: int = 1) -> Question:
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


def _gen_clock_elapsed(diff: int = 1) -> Question:
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


def _gen_cube_stack(diff: int = 1) -> Question:
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


def _gen_cube_view(diff: int = 1) -> Question:
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


def _gen_gfx_shape_classify(diff: int = 1) -> Question:
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


def _gen_gfx_parallelogram(diff: int = 1) -> Question:
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

def _gen_ch_round_up(diff: int = 1) -> Question:
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


def _gen_ch_remainder_max(diff: int = 1) -> Question:
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


def _gen_ch_angle_size(diff: int = 1) -> Question:
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


def _gen_ch_time_diff(diff: int = 1) -> Question:
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

def _gen_vc_div_vertical(diff: int = 1) -> Question:
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


def _gen_vc_mix_detach(diff: int = 1) -> Question:
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


def _gen_vc_3digit_vertical(diff: int = 1) -> Question:
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
# 生成器注册表：能力名 -> (section, 生成器函数, 适用条件lambda)
# ============================================================

GeneratorEntry = tuple[str, Callable, Callable[[GradeProfile], bool]]

GENERATOR_REGISTRY: List[GeneratorEntry] = []


def _register(section: str, fn: Callable, condition: Callable[[GradeProfile], bool]):
    """注册一个生成器"""
    GENERATOR_REGISTRY.append((section, fn, condition))


def _register_all():
    """注册所有生成器（在模块加载时调用）"""
    # -- 一年级口算 --
    _register("oral_calc", _gen_oral_add_1digit,
              lambda p: p.max_number <= 20)
    _register("oral_calc", _gen_oral_sub_1digit,
              lambda p: p.max_number <= 20)
    _register("oral_calc", _gen_oral_add_carry,
              lambda p: p.max_number <= 20)
    _register("oral_calc", _gen_oral_sub_borrow,
              lambda p: p.max_number <= 20)
    _register("oral_calc", _gen_oral_2digit_add_1digit,
              lambda p: p.max_digits >= 2 and not p.supports_multiplication)
    _register("oral_calc", _gen_oral_2digit_sub_1digit,
              lambda p: p.max_digits >= 2 and not p.supports_multiplication)
    _register("oral_calc", _gen_oral_round_add,
              lambda p: p.max_digits >= 2)
    # -- 一年级填空 --
    _register("fill_blank", _gen_fb_num_sequence,
              lambda p: p.max_digits <= 2)
    _register("fill_blank", _gen_fb_compare_num,
              lambda p: True)  # 全年级适用
    _register("fill_blank", _gen_fb_number_name,
              lambda p: p.max_digits <= 2)
    _register("fill_blank", _gen_fb_shape_name,
              lambda p: True)
    _register("fill_blank", _gen_fb_position,
              lambda p: p.max_digits <= 2)
    _register("fill_blank", _gen_fb_clock_hour,
              lambda p: True)

    # -- 二上口算：乘法口诀 --
    _register("oral_calc", _gen_oral_mult_table,
              lambda p: p.supports_multiplication and p.times_table_max > 0
                        and not p.supports_remainder)
    _register("oral_calc", _gen_oral_div_table_basic,
              lambda p: p.supports_division and p.times_table_max > 0
                        and not p.supports_remainder)
    _register("oral_calc", _gen_oral_money,
              lambda p: p.supports_multiplication and p.times_table_max > 0)
    _register("oral_calc", _gen_oral_cm_m,
              lambda p: p.max_digits >= 2 and not p.supports_remainder)
    _register("fill_blank", _gen_fb_mult_meaning,
              lambda p: p.supports_multiplication and p.times_table_max > 0)
    _register("fill_blank", _gen_fb_money_word,
              lambda p: p.supports_multiplication and p.times_table_max > 0)
    # -- 三上：混合运算 + 大数 + 估算 --
    _register("oral_calc", _gen_oral_mix_2step,
              lambda p: p.supports_multiplication and p.max_digits >= 3)
    _register("oral_calc", _gen_oral_mm_cm_km,
              lambda p: p.max_digits >= 3)
    _register("fill_blank", _gen_fb_estimate,
              lambda p: p.max_digits >= 3 and not p.supports_decimals)
    _register("oral_calc", _gen_oral_mult_1digit,
              lambda p: p.supports_multiplication and p.max_digits >= 3)
    # -- 三下：两位数乘法 + 周长 + 分数 --
    _register("oral_calc", _gen_oral_2digit_mult,
              lambda p: p.supports_multiplication and p.max_digits >= 3)
    _register("oral_calc", _gen_oral_div_1digit,
              lambda p: p.supports_division and p.max_digits >= 3)
    _register("fill_blank", _gen_fb_perimeter,
              lambda p: p.supports_multiplication and p.max_digits >= 3)
    _register("fill_blank", _gen_fb_fraction_basic,
              lambda p: p.supports_fractions)
    # -- 四上：大数 + 角度 --
    _register("fill_blank", _gen_fb_large_number,
              lambda p: p.max_digits >= 8)
    _register("fill_blank", _gen_fb_angle_measure,
              lambda p: p.geometry_angles and p.max_digits >= 3)
    # -- 四下~五上：小数 + 三角形 + 方程 + 多边形面积 + 因数 --
    _register("oral_calc", _gen_oral_decimal_add,
              lambda p: p.supports_decimals)
    _register("oral_calc", _gen_oral_decimal_mult,
              lambda p: p.supports_decimals and p.supports_multiplication)
    _register("fill_blank", _gen_fb_triangle,
              lambda p: p.geometry_shapes and p.max_digits >= 3
                        and not p.supports_fractions)
    _register("fill_blank", _gen_fb_equation,
              lambda p: p.supports_multiplication and p.max_digits >= 3)
    _register("fill_blank", _gen_fb_polygon_area,
              lambda p: p.supports_decimals and p.supports_multiplication)
    _register("fill_blank", _gen_fb_factor_multiple,
              lambda p: p.supports_multiplication and p.max_digits >= 3
                        and not p.supports_decimals)
    # -- 五下~六上：分数 + 长方体 + 圆 + 百分数 + 比 --
    _register("oral_calc", _gen_oral_fraction_op,
              lambda p: p.supports_fractions)
    _register("fill_blank", _gen_fb_cuboid,
              lambda p: p.geometry_cubes and p.supports_fractions)
    _register("fill_blank", _gen_fb_circle,
              lambda p: p.supports_fractions and p.supports_decimals)
    _register("oral_calc", _gen_oral_percent,
              lambda p: p.supports_decimals and p.supports_fractions)
    _register("fill_blank", _gen_fb_ratio,
              lambda p: p.supports_fractions and p.supports_decimals)
    # -- 六下：圆柱 + 比例 --
    _register("fill_blank", _gen_fb_cylinder,
              lambda p: p.geometry_cubes and p.supports_fractions)
    _register("fill_blank", _gen_fb_proportion,
              lambda p: p.supports_fractions and p.supports_decimals)

    # -- 口算题 --
    _register("oral_calc", _gen_oral_div_table,
              lambda p: p.supports_division and p.times_table_max > 0)
    _register("oral_calc", _gen_oral_div_remainder,
              lambda p: p.supports_remainder)
    _register("oral_calc", _gen_oral_mix_mult_add,
              lambda p: p.supports_multiplication)
    _register("oral_calc", _gen_oral_mix_div_sub,
              lambda p: p.supports_division)
    _register("oral_calc", _gen_oral_mix_paren,
              lambda p: p.supports_multiplication)
    _register("oral_calc", _gen_oral_length,
              lambda p: len(p.length_units) > 0)
    _register("oral_calc", _gen_oral_3digit_add,
              lambda p: p.max_digits >= 3)
    _register("oral_calc", _gen_oral_3digit_sub,
              lambda p: p.max_digits >= 3)
    _register("oral_calc", _gen_oral_time,
              lambda p: len(p.time_units) > 0)

    # -- 填空题 --
    _register("fill_blank", _gen_fb_remainder_relation,
              lambda p: p.supports_remainder)
    _register("fill_blank", _gen_fb_find_dividend,
              lambda p: p.supports_division)
    _register("fill_blank", _gen_fb_mix_order,
              lambda p: p.supports_multiplication)
    _register("fill_blank", _gen_fb_reading,
              lambda p: p.max_digits >= 4)
    _register("fill_blank", _gen_fb_compare,
              lambda p: p.max_digits >= 3)
    _register("fill_blank", _gen_fb_unit_conv,
              lambda p: len(p.length_units) > 0)
    _register("fill_blank", _gen_fb_length_select,
              lambda p: len(p.length_units) > 0)
    _register("fill_blank", _gen_fb_angle,
              lambda p: p.geometry_angles)
    _register("fill_blank", _gen_fb_clock_walk,
              lambda p: len(p.time_units) >= 2)
    _register("fill_blank", _gen_fb_elapsed_time,
              lambda p: len(p.time_units) >= 2)
    # 图形题生成器（填空）
    _register("fill_blank", _gen_gfx_count_angles,
              lambda p: p.geometry_angles)
    _register("fill_blank", _gen_gfx_angle_identify,
              lambda p: p.geometry_angles)
    _register("fill_blank", _gen_gfx_grid_count,
              lambda p: p.geometry_shapes)
    _register("fill_blank", _gen_clock_read,
              lambda p: len(p.time_units) >= 2)
    _register("fill_blank", _gen_clock_elapsed,
              lambda p: len(p.time_units) >= 2)
    _register("fill_blank", _gen_cube_stack,
              lambda p: p.geometry_cubes)
    _register("fill_blank", _gen_cube_view,
              lambda p: p.geometry_cubes)
    _register("fill_blank", _gen_gfx_shape_classify,
              lambda p: p.geometry_shapes)
    _register("fill_blank", _gen_gfx_parallelogram,
              lambda p: p.geometry_shapes)

    # -- 选择题 --
    _register("choice", _gen_ch_round_up,
              lambda p: p.supports_division)
    _register("choice", _gen_ch_remainder_max,
              lambda p: p.supports_remainder)
    _register("choice", _gen_ch_angle_size,
              lambda p: p.geometry_angles)
    _register("choice", _gen_ch_time_diff,
              lambda p: len(p.time_units) >= 2)

    # -- 竖式计算 --
    _register("vertical_calc", _gen_vc_div_vertical,
              lambda p: p.supports_division)
    _register("vertical_calc", _gen_vc_mix_detach,
              lambda p: p.supports_multiplication)
    _register("vertical_calc", _gen_vc_3digit_vertical,
              lambda p: p.max_digits >= 3)


# 模块加载时执行注册
_register_all()


# ============================================================
# 批量生成入口
# ============================================================

def generate_questions(
    count: int = 30,
    sections: list = None,
    units: list = None,
    grade: int = 2,
    term: int = 2,
) -> List[Question]:
    """
    批量生成题目。根据年级/学期自动筛选适用的生成器。

    参数：
        count: 生成数量
        sections: 限定题型，None=全部
        units: 限定单元，None=全部
        grade: 年级 1-6
        term: 学期 1=上, 2=下
    """
    profile = get_profile(grade, term)

    if sections is None:
        sections = ["oral_calc", "fill_blank", "choice", "vertical_calc", "word_problem"]

    # 从注册表中筛选适用于当前年级的生成器
    active_generators = []
    for section, fn, condition in GENERATOR_REGISTRY:
        if section in sections and condition(profile):
            active_generators.append((fn, section))

    questions = []
    attempts = 0
    max_attempts = count * 3

    while len(questions) < count and attempts < max_attempts:
        attempts += 1

        if "word_problem" in sections and random.random() < 0.15:
            q = _gen_word_problem()
            q.grade = grade
            q.term = term
        elif active_generators:
            fn, _ = random.choice(active_generators)
            try:
                q = fn()
            except Exception:
                continue
            q.grade = grade
            q.term = term
        else:
            q = _gen_word_problem()
            q.grade = grade
            q.term = term

        if units and q.unit not in units:
            continue

        questions.append(q)

    return questions
