"""内置种子题库 - 北师大版二年级下册数学（共8单元，约140题）"""
from .models import Question


def get_all_seed_questions() -> list:
    """返回所有内置种子题目"""
    questions = []

    # ============================================================
    # 一、口算题 (oral_calc) — 约40题，难度1-2
    # ============================================================

    oral = []
    # 第一单元：除法口算
    oral.extend([
        {"unit": 1, "difficulty": 1, "content": "45 ÷ 5 =", "answer": "9", "kp": "表内除法"},
        {"unit": 1, "difficulty": 1, "content": "72 ÷ 8 =", "answer": "9", "kp": "表内除法"},
        {"unit": 1, "difficulty": 1, "content": "63 ÷ 7 =", "answer": "9", "kp": "表内除法"},
        {"unit": 1, "difficulty": 1, "content": "56 ÷ 8 =", "answer": "7", "kp": "表内除法"},
        {"unit": 1, "difficulty": 1, "content": "36 ÷ 6 =", "answer": "6", "kp": "表内除法"},
        {"unit": 1, "difficulty": 1, "content": "81 ÷ 9 =", "answer": "9", "kp": "表内除法"},
        {"unit": 1, "difficulty": 2, "content": "47 ÷ 6 =", "answer": "7...5", "kp": "有余数除法"},
        {"unit": 1, "difficulty": 2, "content": "50 ÷ 7 =", "answer": "7...1", "kp": "有余数除法"},
        {"unit": 1, "difficulty": 2, "content": "38 ÷ 5 =", "answer": "7...3", "kp": "有余数除法"},
        {"unit": 1, "difficulty": 2, "content": "26 ÷ 4 =", "answer": "6...2", "kp": "有余数除法"},
    ])

    # 第二单元：混合运算口算
    oral.extend([
        {"unit": 2, "difficulty": 1, "content": "24 + 8 × 2 =", "answer": "40", "kp": "乘加混合"},
        {"unit": 2, "difficulty": 1, "content": "36 - 4 × 5 =", "answer": "16", "kp": "乘减混合"},
        {"unit": 2, "difficulty": 1, "content": "16 ÷ 4 + 7 =", "answer": "11", "kp": "除加混合"},
        {"unit": 2, "difficulty": 1, "content": "45 ÷ 9 - 3 =", "answer": "2", "kp": "除减混合"},
        {"unit": 2, "difficulty": 2, "content": "6 × 3 + 25 =", "answer": "43", "kp": "乘加混合"},
        {"unit": 2, "difficulty": 2, "content": "50 - 35 ÷ 5 =", "answer": "43", "kp": "除减混合"},
        {"unit": 2, "difficulty": 2, "content": "(12 + 8) ÷ 5 =", "answer": "4", "kp": "括号运算"},
        {"unit": 2, "difficulty": 2, "content": "(30 - 12) ÷ 6 =", "answer": "3", "kp": "括号运算"},
    ])

    # 第四单元：长度单位换算口算
    oral.extend([
        {"unit": 4, "difficulty": 1, "content": "5 dm = ( ) cm", "answer": "50", "kp": "长度换算"},
        {"unit": 4, "difficulty": 1, "content": "4 km = ( ) m", "answer": "4000", "kp": "长度换算"},
        {"unit": 4, "difficulty": 1, "content": "70 mm = ( ) cm", "answer": "7", "kp": "长度换算"},
        {"unit": 4, "difficulty": 2, "content": "8000 m = ( ) km", "answer": "8", "kp": "长度换算"},
        {"unit": 4, "difficulty": 2, "content": "300 cm = ( ) m", "answer": "3", "kp": "长度换算"},
        {"unit": 4, "difficulty": 2, "content": "9 dm = ( ) cm", "answer": "90", "kp": "长度换算"},
    ])

    # 第五单元：整百整十口算
    oral.extend([
        {"unit": 5, "difficulty": 1, "content": "300 + 500 =", "answer": "800", "kp": "整百加减"},
        {"unit": 5, "difficulty": 1, "content": "1200 - 700 =", "answer": "500", "kp": "整百加减"},
        {"unit": 5, "difficulty": 1, "content": "650 + 350 =", "answer": "1000", "kp": "整百加减"},
        {"unit": 5, "difficulty": 1, "content": "1000 - 460 =", "answer": "540", "kp": "整百加减"},
        {"unit": 5, "difficulty": 2, "content": "278 + 356 =", "answer": "634", "kp": "三位数加法"},
        {"unit": 5, "difficulty": 2, "content": "604 - 287 =", "answer": "317", "kp": "三位数减法"},
        {"unit": 5, "difficulty": 2, "content": "480 + 190 =", "answer": "670", "kp": "三位数加法"},
        {"unit": 5, "difficulty": 2, "content": "703 - 456 =", "answer": "247", "kp": "三位数减法"},
    ])

    # 第七单元：时间换算口算
    oral.extend([
        {"unit": 7, "difficulty": 1, "content": "1 时 = ( ) 分", "answer": "60", "kp": "时间换算"},
        {"unit": 7, "difficulty": 1, "content": "1 分 = ( ) 秒", "answer": "60", "kp": "时间换算"},
        {"unit": 7, "difficulty": 1, "content": "1 时 20 分 = ( ) 分", "answer": "80", "kp": "时间换算"},
        {"unit": 7, "difficulty": 2, "content": "90 秒 = ( ) 分 ( ) 秒", "answer": "1分30秒", "kp": "时间换算"},
        {"unit": 7, "difficulty": 2, "content": "2 分 15 秒 = ( ) 秒", "answer": "135", "kp": "时间换算"},
        {"unit": 7, "difficulty": 2, "content": "75 分 = ( ) 时 ( ) 分", "answer": "1时15分", "kp": "时间换算"},
    ])

    for item in oral:
        questions.append(Question(
            unit=item["unit"], section="oral_calc", difficulty=item["difficulty"],
            content=item["content"], answer=item["answer"],
            knowledge_point=item["kp"], tags=item.get("tags", ""),
        ))

    # ============================================================
    # 二、填空题 (fill_blank) — 约35题，难度1-4
    # ============================================================

    fb = []
    # 第一单元
    fb.extend([
        {"unit": 1, "diff": 2, "content": "在（   ）÷ 6 = 7 …… 3 中，被除数是（   ）。", "answer": "45", "kp": "有余数除法"},
        {"unit": 1, "diff": 3, "content": "一个数除以 5，余数可能是（   ），余数最大是（   ）。", "answer": "1,2,3,4；4", "kp": "余数与除数关系"},
        {"unit": 1, "diff": 3, "content": "在（   ）÷（   ）= 5 …… 4 中，除数最小是（   ），这时被除数是（   ）。", "answer": "5；29", "kp": "有余数除法逆向"},
        {"unit": 1, "diff": 4, "content": "有一些苹果，比 30 个多，比 40 个少，平均分给 7 个小朋友，还剩 2 个，苹果有（   ）个。", "answer": "37", "kp": "有余数除法综合"},
    ])

    # 第二单元
    fb.extend([
        {"unit": 2, "diff": 2, "content": "计算 45 − 18 ÷ 3 时，先算（   ）法，再算（   ）法，结果是（   ）。", "answer": "除；减；39", "kp": "运算顺序"},
        {"unit": 2, "diff": 2, "content": "把 40 ÷ 8 = 5 和 5 + 10 = 15 合并成综合算式：（                   ）。", "answer": "40÷8+10=15", "kp": "综合算式"},
        {"unit": 2, "diff": 3, "content": "在括号里填合适的数：6 ×（   ）+ 4 = 34", "answer": "5", "kp": "混合运算逆向"},
        {"unit": 2, "diff": 3, "content": "运算顺序是先括号，再（   ），最后（   ）。", "answer": "乘除；加减", "kp": "运算顺序"},
    ])

    # 第三单元
    fb.extend([
        {"unit": 3, "diff": 1, "content": "3682 读作（                      ）。", "answer": "三千六百八十二", "kp": "万以内数读法"},
        {"unit": 3, "diff": 1, "content": "六千零五十 写作（      ）。", "answer": "6050", "kp": "万以内数写法"},
        {"unit": 3, "diff": 2, "content": "7050 读作（                      ），它是由（   ）个千和（   ）个十组成的。", "answer": "七千零五十；7；5", "kp": "数的组成"},
        {"unit": 3, "diff": 2, "content": "在 3208、3820、3028、3802 中，最大的数是（      ），最小的数是（      ）。", "answer": "3820；3028", "kp": "数的大小比较"},
        {"unit": 3, "diff": 3, "content": "用两个 0 和两个 5 组成四位数：只读一个零的数是（        ）和（        ）。", "answer": "5005；5050", "kp": "组数问题"},
        {"unit": 3, "diff": 4, "content": "一个四位数，百位上是最大的一位数，十位比百位小 3，个位是 0，千位是 1，这个数是（      ）。", "answer": "1960", "kp": "按条件组数"},
    ])

    # 第四单元
    fb.extend([
        {"unit": 4, "diff": 1, "content": "5 m =（    ）dm     3 km =（    ）m     40 cm =（    ）dm", "answer": "50；3000；4", "kp": "长度单位换算"},
        {"unit": 4, "diff": 2, "content": "在括号里填合适的单位：课桌高约 7（    ），大象高约 3（    ），橡皮厚约 8（    ）。", "answer": "dm；m；mm", "kp": "长度单位选择"},
        {"unit": 4, "diff": 3, "content": "一枝铅笔长 2 dm，用去 5 cm，还剩（    ）cm。", "answer": "15", "kp": "长度计算"},
        {"unit": 4, "diff": 3, "content": "从家到学校 800 m，已经走了 450 m，还剩（    ）m。", "answer": "350", "kp": "长度应用"},
    ])

    # 第五单元
    fb.extend([
        {"unit": 5, "diff": 2, "content": "478 + 265，个位 8 + 5 = 13，向（    ）位进 1，个位写（    ）。", "answer": "十；3", "kp": "进位加法"},
        {"unit": 5, "diff": 2, "content": "703 − 258，个位不够减，从（    ）位退 1 当 10，个位变成 13 减 8。", "answer": "十", "kp": "退位减法"},
        {"unit": 5, "diff": 3, "content": "一个加数是 348，和是 600，另一个加数是（    ）。", "answer": "252", "kp": "加减法逆向"},
        {"unit": 5, "diff": 3, "content": "比 456 多 278 的数是（    ）；比 800 少 365 的数是（    ）。", "answer": "734；435", "kp": "比多比少"},
    ])

    # 第六单元
    fb.extend([
        {"unit": 6, "diff": 1, "content": "角有一个（    ）和两条（    ）。角的大小与两边的（          ）有关。", "answer": "顶点；边；张口大小", "kp": "角的认识"},
        {"unit": 6, "diff": 1, "content": "长方形有（    ）条边，对边（    ），四个角都是（    ）角。", "answer": "4；相等；直", "kp": "长方形特征"},
        {"unit": 6, "diff": 2, "content": "正方形是特殊的（              ）。长方形是特殊的（                  ）。", "answer": "长方形；平行四边形", "kp": "图形关系"},
        {"unit": 6, "diff": 2, "content": "比直角小的角叫（    ）角，比直角大的角叫（    ）角。", "answer": "锐；钝", "kp": "角的分类"},
        {"unit": 6, "diff": 3, "content": "一个长方形中剪去一个角，剩下的图形可能有（    ）个角、（    ）个角或（    ）个角。", "answer": "3；4；5", "kp": "图形探究"},
    ])

    # 第七单元
    fb.extend([
        {"unit": 7, "diff": 2, "content": "分针从 12 走到 5，走了（    ）分；时针从 3 走到 8，经过了（    ）时。", "answer": "25；5", "kp": "钟面走动"},
        {"unit": 7, "diff": 2, "content": "小明 7:30 从家出发，7:54 到校，路上用了（    ）分。", "answer": "24", "kp": "经过时间"},
        {"unit": 7, "diff": 3, "content": "钟面上显示 3:20，再过（    ）分就是 4:00。", "answer": "40", "kp": "倒推时间"},
    ])

    # 第八单元
    fb.extend([
        {"unit": 8, "diff": 1, "content": "在统计中，用「正」字法记录数据，一个「正」字代表（    ）人。", "answer": "5", "kp": "统计方法"},
        {"unit": 8, "diff": 2, "content": "统计全班最喜欢的颜色：红色有 15 人，蓝色有 8 人，红色比蓝色多（    ）人。", "answer": "7", "kp": "数据分析"},
    ])

    for item in fb:
        questions.append(Question(
            unit=item["unit"], section="fill_blank", difficulty=item["diff"],
            content=item["content"], answer=item["answer"],
            knowledge_point=item["kp"], tags=item.get("tags", ""),
        ))

    # ============================================================
    # 三、选择题 (choice) — 约25题，难度2-4
    # ============================================================

    ch = []
    ch.extend([
        {"unit": 1, "diff": 2, "content": "有 23 个苹果，每盘放 5 个，至少需要（    ）个盘子。",
         "answer": "B", "opts": ["A. 4", "B. 5", "C. 6", "D. 23"], "kp": "进一法"},
        {"unit": 1, "diff": 2, "content": "53 颗扣子，每件衣服钉 8 颗，最多能钉（    ）件衣服。",
         "answer": "A", "opts": ["A. 6", "B. 7", "C. 8", "D. 5"], "kp": "去尾法"},
        {"unit": 1, "diff": 3, "content": "下面算式中，余数最大的是（    ）。",
         "answer": "B", "opts": ["A. 20÷6", "B. 23÷4", "C. 35÷7", "D. 40÷8"], "kp": "余数比较"},
        {"unit": 1, "diff": 3, "content": "一个数除以 6，商是 5，余数可能是（    ）。",
         "answer": "D", "opts": ["A. 5", "B. 6", "C. 7", "D. 0~5"], "kp": "余数范围"},
        {"unit": 2, "diff": 2, "content": "下面算式中，运算顺序正确的是（    ）。",
         "answer": "A", "opts": ["A. 24+8÷4=24+2=26", "B. 24+8÷4=32÷4=8", "C. 24+8÷4=28÷4=7"], "kp": "运算顺序"},
        {"unit": 2, "diff": 3, "content": "面包每个 3 元，饮料每瓶 6 元。买 4 个面包和 1 瓶饮料，应付（    ）元。",
         "answer": "C", "opts": ["A. 12", "B. 15", "C. 18", "D. 24"], "kp": "乘加应用"},
        {"unit": 3, "diff": 2, "content": "7050 读作（    ）。",
         "answer": "B", "opts": ["A. 七千零五", "B. 七千零五十", "C. 七千零零五十", "D. 七百五十"], "kp": "读数"},
        {"unit": 3, "diff": 2, "content": "下面各数中，一个零都不读的是（    ）。",
         "answer": "A", "opts": ["A. 4000", "B. 4005", "C. 4050", "D. 4005"], "kp": "0的读法"},
        {"unit": 3, "diff": 3, "content": "用 5、0、2、8 四个数字组成最大的四位数是（    ）。",
         "answer": "C", "opts": ["A. 5280", "B. 8052", "C. 8520", "D. 8526"], "kp": "组最大数"},
        {"unit": 4, "diff": 2, "content": "下面长度最长的是（    ）。",
         "answer": "B", "opts": ["A. 2 km", "B. 2000 m", "C. 200 dm", "D. 2 m"], "kp": "长度比较"},
        {"unit": 4, "diff": 2, "content": "课桌高约（    ）。",
         "answer": "C", "opts": ["A. 7 km", "B. 7 m", "C. 7 dm", "D. 7 mm"], "kp": "单位选择"},
        {"unit": 4, "diff": 3, "content": "小明沿操场跑了 500 米，再跑（    ）米就是 1 千米。",
         "answer": "A", "opts": ["A. 500", "B. 1500", "C. 100", "D. 50"], "kp": "长度计算"},
        {"unit": 5, "diff": 2, "content": "下面算式中，结果比 500 大的是（    ）。",
         "answer": "D", "opts": ["A. 300+150", "B. 200+280", "C. 800-450", "D. 280+280"], "kp": "估算"},
        {"unit": 5, "diff": 3, "content": "一个加数是 348，和是 600，另一个加数是（    ）。",
         "answer": "B", "opts": ["A. 262", "B. 252", "C. 362", "D. 352"], "kp": "加减法逆向"},
        {"unit": 5, "diff": 4, "content": "被减数增加 20，减数减少 20，差（    ）。",
         "answer": "C", "opts": ["A. 减少40", "B. 不变", "C. 增加40", "D. 增加20"], "kp": "差的变化规律"},
        {"unit": 6, "diff": 2, "content": "角的大小与（    ）有关。",
         "answer": "B", "opts": ["A. 边的长短", "B. 张口的大小", "C. 顶点的位置", "D. 以上都不是"], "kp": "角的大小"},
        {"unit": 6, "diff": 2, "content": "下面说法正确的是（    ）。",
         "answer": "C", "opts": ["A. 对边相等的四边形是长方形", "B. 长方形是特殊的正方形", "C. 正方形是特殊的长方形", "D. 平行四边形四个角都是直角"], "kp": "图形关系"},
        {"unit": 6, "diff": 3, "content": "一个三角尺上有（    ）个直角。",
         "answer": "A", "opts": ["A. 1", "B. 2", "C. 3", "D. 0"], "kp": "直角认识"},
        {"unit": 7, "diff": 2, "content": "分针从 2 走到 6，经过了（    ）分。",
         "answer": "B", "opts": ["A. 4", "B. 20", "C. 15", "D. 10"], "kp": "指针走动"},
        {"unit": 7, "diff": 3, "content": "电影从 9:30 开始，到 11:25 结束，放映了（    ）。",
         "answer": "D", "opts": ["A. 2时", "B. 1时55分", "C. 2时5分", "D. 2时55分"], "kp": "经过时间"},
        {"unit": 7, "diff": 3, "content": "跑 60 米，小红 14 秒，小英 12 秒，小云 13 秒，谁跑得最快？（    ）",
         "answer": "A", "opts": ["A. 小英", "B. 小红", "C. 小云", "D. 一样快"], "kp": "时间比较"},
        {"unit": 8, "diff": 2, "content": "下表是二(1)班喜欢的运动统计：跑步12人，跳绳15人，踢球8人。喜欢跳绳的比踢球的多（    ）人。",
         "answer": "B", "opts": ["A. 3", "B. 7", "C. 8", "D. 15"], "kp": "数据分析"},
        {"unit": 8, "diff": 3, "content": "在班级三好学生投票中，小明的「正」字记录比小红多 2 画，则小明比小红多（    ）票。",
         "answer": "C", "opts": ["A. 5", "B. 10", "C. 2", "D. 4"], "kp": "正字统计"},
        {"unit": 3, "diff": 1, "content": "一百一百地数，九百后面的第一个数是（    ）。",
         "answer": "A", "opts": ["A. 一千", "B. 九百零一", "C. 八百九十九", "D. 一千零一"], "kp": "数数"},
        {"unit": 6, "diff": 2, "content": "下面图形中是平行四边形的是（    ）。",
         "answer": "D", "opts": ["A. 梯形", "B. 三角形", "C. 五角星", "D. 拉开的栅栏门形状"], "kp": "平行四边形"},
    ])

    for item in ch:
        import json
        questions.append(Question(
            unit=item["unit"], section="choice", difficulty=item["diff"],
            content=item["content"], answer=item["answer"],
            options=json.dumps(item["opts"], ensure_ascii=False),
            knowledge_point=item["kp"], tags=item.get("tags", ""),
        ))

    # ============================================================
    # 四、竖式/脱式计算 (vertical_calc) — 约20题，难度2-5
    # ============================================================

    vc = []
    # 第一单元：有余数除法竖式
    vc.extend([
        {"unit": 1, "diff": 2, "content": "用竖式计算：47 ÷ 7 =", "answer": "6...5", "kp": "有余数除法竖式"},
        {"unit": 1, "diff": 2, "content": "用竖式计算：58 ÷ 8 =", "answer": "7...2", "kp": "有余数除法竖式"},
        {"unit": 1, "diff": 2, "content": "用竖式计算：66 ÷ 9 =", "answer": "7...3", "kp": "有余数除法竖式"},
        {"unit": 1, "diff": 3, "content": "用竖式计算并验算：73 ÷ 6 =", "answer": "12...1", "kp": "有余数除法验算"},
    ])

    # 第二单元：脱式计算
    vc.extend([
        {"unit": 2, "diff": 2, "content": "脱式计算：6 × 8 + 34", "answer": "82", "kp": "脱式计算"},
        {"unit": 2, "diff": 2, "content": "脱式计算：45 ÷ 5 - 3", "answer": "6", "kp": "脱式计算"},
        {"unit": 2, "diff": 3, "content": "脱式计算：(45 - 18) × 3", "answer": "81", "kp": "脱式计算带括号"},
        {"unit": 2, "diff": 3, "content": "脱式计算：72 ÷ (3 + 6)", "answer": "8", "kp": "脱式计算带括号"},
        {"unit": 2, "diff": 4, "content": "脱式计算：(38 + 27) ÷ 5 + 16", "answer": "29", "kp": "多步脱式"},
        {"unit": 2, "diff": 4, "content": "脱式计算：90 - (54 ÷ 9) × 7", "answer": "48", "kp": "多步脱式"},
        {"unit": 2, "diff": 5, "content": "脱式计算：(100 - 72) ÷ 4 × 3", "answer": "21", "kp": "综合脱式"},
    ])

    # 第五单元：三位数加减竖式
    vc.extend([
        {"unit": 5, "diff": 2, "content": "用竖式计算：278 + 356 =", "answer": "634", "kp": "三位数加法竖式"},
        {"unit": 5, "diff": 2, "content": "用竖式计算：604 - 287 =", "answer": "317", "kp": "三位数减法竖式"},
        {"unit": 5, "diff": 3, "content": "用竖式计算并验算：456 + 389 =", "answer": "845", "kp": "连续进位加"},
        {"unit": 5, "diff": 3, "content": "用竖式计算并验算：700 - 356 =", "answer": "344", "kp": "连续退位减"},
        {"unit": 5, "diff": 4, "content": "用竖式计算：638 - 279 + 165 =", "answer": "524", "kp": "加减混合竖式"},
        {"unit": 5, "diff": 4, "content": "用竖式计算：508 + 296 - 187 =", "answer": "617", "kp": "加减混合竖式"},
        {"unit": 5, "diff": 5, "content": "用竖式计算：800 - 237 - 418 =", "answer": "145", "kp": "连减竖式"},
        {"unit": 5, "diff": 5, "content": "用竖式计算：356 + 178 + 265 =", "answer": "799", "kp": "连加竖式"},
    ])

    for item in vc:
        questions.append(Question(
            unit=item["unit"], section="vertical_calc", difficulty=item["diff"],
            content=item["content"], answer=item["answer"],
            knowledge_point=item["kp"], tags=item.get("tags", ""),
        ))

    # ============================================================
    # 五、解决问题 (word_problem) — 约20题，难度3-5
    # ============================================================

    wp = []
    # 第一单元应用题
    wp.extend([
        {"unit": 1, "diff": 3, "content": "二(1)班有 42 名同学去划船，每条船最多坐 5 人。他们至少需要租几条船？",
         "answer": "42÷5=8(条)……2(人), 8+1=9(条)", "kp": "进一法"},
        {"unit": 1, "diff": 3, "content": "妈妈买了 53 个扣子，每件衣服需要钉 8 颗扣子。最多可以钉几件衣服？",
         "answer": "53÷8=6(件)……5(颗), 最多钉6件", "kp": "去尾法"},
        {"unit": 1, "diff": 4, "content": "有 28 个气球，每 6 个扎成一束。最多可以扎几束？至少再加几个气球才能再扎一束？",
         "answer": "28÷6=4(束)……4(个)；6-4=2(个)", "kp": "有余数综合"},
    ])

    # 第二单元应用题
    wp.extend([
        {"unit": 2, "diff": 3, "content": "面包每个 3 元，饮料每瓶 6 元。买 4 个面包和 1 瓶饮料，应付多少元？",
         "answer": "3×4=12(元), 12+6=18(元)", "kp": "乘加两步"},
        {"unit": 2, "diff": 4, "content": "小明带了 30 元，买了 3 个笔记本（每个 4 元），还剩多少元？如果再买 2 支笔（每支 3 元），钱够吗？",
         "answer": "3×4=12(元), 30-12=18(元)；2×3=6(元), 18>6,够", "kp": "多步购物"},
        {"unit": 2, "diff": 4, "content": "学校有 72 本书，平均分给 8 个班。每个班分到几本书？如果每班再拿走 3 本，一共拿走多少本？",
         "answer": "72÷8=9(本)；9+3=12(本)", "kp": "除加两步"},
    ])

    # 第四单元应用题
    wp.extend([
        {"unit": 4, "diff": 3, "content": "一枝铅笔长 2 dm，用去 5 cm，还剩多长？",
         "answer": "2dm=20cm, 20-5=15(cm)", "kp": "长度换算应用"},
        {"unit": 4, "diff": 3, "content": "小明家离学校 1 km，他走了 400 m，还要走多少米到学校？",
         "answer": "1km=1000m, 1000-400=600(m)", "kp": "长度换算应用"},
    ])

    # 第五单元应用题
    wp.extend([
        {"unit": 5, "diff": 3, "content": "图书馆有故事书 365 本，科技书比故事书少 128 本。科技书有多少本？",
         "answer": "365-128=237(本)", "kp": "比多比少"},
        {"unit": 5, "diff": 4, "content": "图书馆有故事书 365 本，科技书比故事书少 128 本。两种书一共有多少本？",
         "answer": "365-128=237(本), 365+237=602(本)", "kp": "多步加减"},
        {"unit": 5, "diff": 4, "content": "超市原有苹果 458 千克，上午卖出 189 千克，下午又运进 276 千克。现在有多少千克苹果？",
         "answer": "458-189=269(kg), 269+276=545(kg)", "kp": "加减混合应用"},
        {"unit": 5, "diff": 5, "content": "小红家、小明家和学校在同一条路上。小红家离学校 358 米，小明家比小红家离学校远 167 米。小红家和小明家最多相距多少米？最少呢？",
         "answer": "最远(在两侧):358+167=525, 358+525=883(米)；最近(同侧): 358+167-358=525-358=167(米)(注: 实际上小红358 小明525,最近在两侧=358+525=883 同侧=|525-358|=167", "kp": "位置关系综合"},
    ])

    # 第七单元应用题
    wp.extend([
        {"unit": 7, "diff": 3, "content": "小明 7:30 从家出发去学校，走到学校用了 24 分钟。小明几时几分到校？",
         "answer": "7:30+24分=7:54", "kp": "结束时间"},
        {"unit": 7, "diff": 4, "content": "一节课 40 分钟，第一节课 8:20 开始。什么时候下课？课间休息 10 分钟后，第二节课什么时间开始？",
         "answer": "8:20+40分=9:00下课；9:00+10分=9:10开始", "kp": "时间推算"},
        {"unit": 7, "diff": 4, "content": "电影 9:30 开始，11:25 结束。电影放映了多长时间？",
         "answer": "11:25-9:30=1时55分", "kp": "经过时间"},
    ])

    # 第六单元应用题
    wp.extend([
        {"unit": 6, "diff": 3, "content": "一根铁丝可以围成一个长 6 cm、宽 4 cm 的长方形。这根铁丝长多少厘米？",
         "answer": "(6+4)×2=20(cm)", "kp": "长方形周长入门"},
    ])

    # 第三单元应用题
    wp.extend([
        {"unit": 3, "diff": 4, "content": "用 3、0、5、8 可以组成多少个不同的四位数？（要求不能以 0 开头）其中最大的数和最小的数相差多少？",
         "answer": "3×3×2×1=18(个)；8530-3058=5472", "kp": "组数问题"},
    ])

    # 综合应用题
    wp.extend([
        {"unit": 5, "diff": 5, "content": "一本书有 278 页，小明第一天看了 55 页，第二天比第一天多看 18 页。两天一共看了多少页？还剩多少页没看？",
         "answer": "55+18=73(页), 55+73=128(页)；278-128=150(页)", "kp": "多步综合"},
        {"unit": 7, "diff": 5, "content": "小明从家到学校要走 15 分钟。学校 8:00 上课，小明最迟应该几点几分从家出发？小明每天来回两趟，共走了多少分钟？",
         "answer": "8:00-15分=7:45出发；15×4=60(分)", "kp": "时间综合"},
    ])

    for item in wp:
        questions.append(Question(
            unit=item["unit"], section="word_problem", difficulty=item["diff"],
            content=item["content"], answer=item["answer"],
            knowledge_point=item["kp"], tags=item.get("tags", ""),
        ))

    # ============================================================
    # 六、图形题 (graphics) — 约20题，用表格+Unicode渲染几何图形
    # ============================================================

    gfx = []

    # --- 角的识别 ---
    gfx.extend([
        {"unit": 6, "diff": 1, "section": "fill_blank",
         "content": "用三角尺比一比，下面的角各是什么角？",
         "answer": "钝角；锐角；直角",
         "kp": "角的分类",
         "tags": "图形,角识别",
         "graphic": {
             "type": "angle_identify",
             "angles": [
                 {"symbol": "╲", "label": "第1个"},
                 {"symbol": "∠", "label": "第2个"},
                 {"symbol": "┌", "label": "第3个"},
             ]
         }},
        {"unit": 6, "diff": 1, "section": "fill_blank",
         "content": "下面的图形中，哪些是角？在括号里打√，不是的打×。",
         "answer": "√；×；√；×",
         "kp": "角的认识",
         "tags": "图形,角识别",
         "graphic": {
             "type": "angle_judge",
             "shapes": [
                 {"symbol": "∠", "label": "①"},
                 {"symbol": "┐┌", "label": "②"},
                 {"symbol": "∟", "label": "③"},
                 {"symbol": "╱", "label": "④"},
             ]
         }},
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "下面各有几个角？填在括号里。",
         "answer": "3；4；5；6",
         "kp": "数角",
         "tags": "图形,数角",
         "graphic": {
             "type": "count_angles",
             "shapes": [
                 {"symbol": "△", "label": "三角形"},
                 {"symbol": "□", "label": "正方形"},
                 {"symbol": "⬠", "label": "五边形"},
                 {"symbol": "⬡", "label": "六边形"},
             ]
         }},
    ])

    # --- 直角/锐角/钝角 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "choice",
         "content": "下图中有几个直角？",
         "answer": "B",
         "kp": "数直角",
         "tags": "图形,直角",
         "options": '["A. 2个", "B. 4个", "C. 6个", "D. 8个"]',
         "graphic": {
             "type": "grid_count",
             "rows": 2, "cols": 2,
             "description": "长方形被分成4个小长方形"
         }},
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "三角尺上有（    ）个角，其中有（    ）个直角。",
         "answer": "3；1",
         "kp": "直角认识",
         "tags": "图形,三角尺"},
        {"unit": 6, "diff": 3, "section": "choice",
         "content": "把一个长方形剪去一个角，剩下的图形不可能有几个角？",
         "answer": "C",
         "kp": "图形探究",
         "tags": "图形,剪角",
         "options": '["A. 3个", "B. 4个", "C. 2个", "D. 5个"]'},
    ])

    # --- 长方形/正方形 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "下图中有几个长方形？",
         "answer": "9",
         "kp": "数长方形",
         "tags": "图形,数长方形",
         "graphic": {
             "type": "grid_count",
             "rows": 2, "cols": 3,
             "description": "2行×3列的方格，共有多少个长方形"
         }},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "数一数，下图中有（    ）个长方形，（    ）个正方形，（    ）个平行四边形。",
         "answer": "5；2；2",
         "kp": "数图形",
         "tags": "图形,综合计数",
         "graphic": {
             "type": "grid_count",
             "rows": 2, "cols": 2,
             "description": "2×2正方形网格，标注边长相等"
         }},
        {"unit": 6, "diff": 2, "section": "choice",
         "content": "下面图形中，四个角都是直角的是（    ）。",
         "answer": "C",
         "kp": "直角特征",
         "tags": "图形,直角判断",
         "options": '["A. 平行四边形", "B. 梯形", "C. 长方形", "D. 菱形"]'},
    ])

    # --- 平行四边形 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "平行四边形有（    ）条边，对边（    ），它容易（    ）。",
         "answer": "4；相等；变形",
         "kp": "平行四边形特征",
         "tags": "图形,平行四边形"},
        {"unit": 6, "diff": 3, "section": "choice",
         "content": "拉一拉长方形木框，变成平行四边形后，什么变了？什么没变？",
         "answer": "C",
         "kp": "平行四边形特性",
         "tags": "图形,变形",
         "options": '["A. 边长变了", "B. 角没变", "C. 形状变了，边长没变", "D. 都变了"]'},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "七巧板中，有（    ）种不同的图形，分别是（                            ）。",
         "answer": "3；三角形、正方形、平行四边形",
         "kp": "七巧板",
         "tags": "图形,七巧板"},
    ])

    # --- 图形拼组 ---
    gfx.extend([
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "两个完全一样的三角形可以拼成一个（                ）。",
         "answer": "平行四边形",
         "kp": "图形拼组",
         "tags": "图形,拼组"},
        {"unit": 6, "diff": 4, "section": "word_problem",
         "content": "一个长方形长 8 cm、宽 5 cm，在它里面画一个最大的正方形。这个正方形的边长是多少厘米？剩下的部分是什么图形？",
         "answer": "5cm；长方形（长5cm宽3cm）",
         "kp": "图形综合",
         "tags": "图形,最大正方形"},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "最少用（    ）个相同的小正方形可以拼成一个大正方形。",
         "answer": "4",
         "kp": "图形拼组",
         "tags": "图形,拼正方形"},
    ])

    # --- 画图操作题 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "在方格纸上画一个长方形和一个正方形。",
         "answer": "（略）",
         "kp": "画图形",
         "tags": "图形,画图",
         "graphic": {
             "type": "draw_grid",
             "rows": 4, "cols": 8,
             "description": "4×8的方格纸，供画图使用"
         }},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "画一个比直角小的角。",
         "answer": "（略）",
         "kp": "画角",
         "tags": "图形,画角",
         "graphic": {
             "type": "draw_angle",
         }},
    ])

    # --- 观察物体 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "choice",
         "content": "从不同方向观察一个长方体，最多能看到（    ）个面。",
         "answer": "C",
         "kp": "观察物体",
         "tags": "图形,观察",
         "options": '["A. 2个", "B. 4个", "C. 3个", "D. 1个"]'},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "用 4 个相同的小正方体可以拼成（    ）种不同的长方体。",
         "answer": "2",
         "kp": "立体拼组",
         "tags": "图形,拼组"},
    ])

    # --- 钟面读时 ---
    gfx.extend([
        {"unit": 7, "diff": 1, "section": "fill_blank",
         "content": "写出下面钟面上的时间。",
         "answer": "3:00；7:30；11:15；5:45",
         "kp": "读钟面",
         "tags": "图形,钟面,时钟",
         "graphic": {
             "type": "clock",
             "clocks": [
                 {"hour": 3, "minute": 0},
                 {"hour": 7, "minute": 30},
                 {"hour": 11, "minute": 15},
                 {"hour": 5, "minute": 45},
             ]
         }},
        {"unit": 7, "diff": 2, "section": "fill_blank",
         "content": "看图写出钟面上的时间，再算一算经过了多少时间。",
         "answer": "8:00→8:30→9:00；经过30分；经过30分",
         "kp": "经过时间",
         "tags": "图形,钟面,经过时间",
         "graphic": {
             "type": "clock",
             "clocks": [
                 {"hour": 8, "minute": 0},
                 {"hour": 8, "minute": 30},
                 {"hour": 9, "minute": 0},
             ]
         }},
        {"unit": 7, "diff": 2, "section": "fill_blank",
         "content": "根据时间画出时针和分针。",
         "answer": "（略）",
         "kp": "画钟面",
         "tags": "图形,钟面,画时针分针",
         "graphic": {
             "type": "clock_time",
             "times": [
                 {"time": "4:00", "label": "4时"},
                 {"time": "10:30", "label": "10时30分"},
                 {"time": "6:15", "label": "6时15分"},
             ]
         }},
    ])

    # --- 立方体堆叠 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "数一数，下面的图形由几个小立方体搭成？",
         "answer": "6",
         "kp": "数立方体",
         "tags": "图形,立方体,堆叠",
         "graphic": {
             "type": "cube_stack",
             "grid": [[2, 1], [2, 1]],
         }},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "数一数，下面这堆积木一共有多少个？",
         "answer": "9",
         "kp": "数立方体",
         "tags": "图形,立方体,堆叠",
         "graphic": {
             "type": "cube_stack",
             "grid": [[3, 2, 1], [1, 1, 0], [1, 0, 0]],
         }},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "下面是用小正方体搭成的立体图形。请根据从不同方向看到的形状填空。",
         "answer": "7",
         "kp": "三视图",
         "tags": "图形,立方体,三视图",
         "graphic": {
             "type": "cube_view",
             "front": [3, 2, 1],
             "side": [2, 1, 1],
         }},
        {"unit": 6, "diff": 4, "section": "word_problem",
         "content": "用一些小正方体搭成一个长方体。从正面看是3层2列，从侧面看是2层3列。最少需要几个小正方体？",
         "answer": "最少18个（3×2×3）",
         "kp": "三视图推理",
         "tags": "图形,立方体,三视图推理"},
    ])

    # --- 图形分类 (shape_classify) ---
    gfx.extend([
        {"unit": 6, "diff": 1, "section": "fill_blank",
         "content": "写出下面图形的名称。",
         "answer": "长方形；正方形；平行四边形；三角形",
         "kp": "图形识别",
         "tags": "图形,图形分类",
         "graphic": {
             "type": "shape_classify",
             "shapes": [
                 {"symbol": "▭", "label": ""},
                 {"symbol": "□", "label": ""},
                 {"symbol": "▱", "label": ""},
                 {"symbol": "△", "label": ""},
             ]
         }},
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "下面哪些图形是平行四边形？在括号里打√，不是的打×。",
         "answer": "×；√；×；√",
         "kp": "平行四边形识别",
         "tags": "图形,图形分类",
         "graphic": {
             "type": "shape_classify",
             "shapes": [
                 {"symbol": "□", "label": "①"},
                 {"symbol": "▱", "label": "②"},
                 {"symbol": "▭", "label": "③"},
                 {"symbol": "▱", "label": "④"},
             ]
         }},
        {"unit": 6, "diff": 2, "section": "choice",
         "content": "下面哪个图形不是四边形？",
         "answer": "C",
         "kp": "四边形识别",
         "tags": "图形,图形分类,四边形",
         "options": '["A. 长方形", "B. 平行四边形", "C. 三角形", "D. 正方形"]'},
    ])

    # --- 七巧板 (tangram) ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "下面是用七巧板拼出的小房子。数一数，每种颜色的图形分别是什么形状？",
         "answer": "红色三角形；蓝色正方形；绿色平行四边形",
         "kp": "七巧板认识",
         "tags": "图形,七巧板,分类",
         "graphic": {
             "type": "tangram",
             "pieces": [
                 ["大三角形", "r"], ["大三角形", "r"],
                 ["中三角形", "b"], ["小三角形", "g"],
                 ["小三角形", "g"], ["正方形", "y"],
                 ["平行四边形", "p"],
             ],
             "grid": [
                 [0,   0,   0,   "r", "r", 0,   0],
                 [0,   0,   "b", "b", "b", 0,   0],
                 [0,   "g", "g", "y", "y", "r", "r"],
                 [0,   "g", "p", "p", "y", "y", 0],
                 ["g", "g", "p", "p", 0,   0,   0],
             ]
         }},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "用一副七巧板拼一拼。两个完全一样的三角形可以拼成什么图形？写出三种可能。",
         "answer": "正方形；平行四边形；大三角形",
         "kp": "七巧板拼组",
         "tags": "图形,七巧板,拼组"},
        {"unit": 6, "diff": 3, "section": "choice",
         "content": "七巧板中，共有几块三角形？",
         "answer": "B",
         "kp": "七巧板组成",
         "tags": "图形,七巧板",
         "options": '["A. 3块", "B. 5块", "C. 7块", "D. 4块"]'},
    ])

    # --- 平行四边形变形 + 拼组 ---
    gfx.extend([
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "看一看，长方形拉成平行四边形后，什么变了？什么没变？",
         "answer": "形状变了（角变了），边长没变",
         "kp": "平行四边形特性",
         "tags": "图形,平行四边形,变形",
         "graphic": {
             "type": "parallelogram",
         }},
        {"unit": 6, "diff": 2, "section": "fill_blank",
         "content": "两个完全一样的直角三角形可以拼成一个（                ）形。",
         "answer": "长方形",
         "kp": "图形拼组",
         "tags": "图形,拼组,直角三角形"},
        {"unit": 6, "diff": 3, "section": "word_problem",
         "content": "一张长方形纸长10cm、宽6cm。小明沿对角线剪开，得到两个完全一样的三角形。每个三角形的三个角分别是什么角？",
         "answer": "1个直角、1个锐角、1个锐角（或锐角、钝角看具体情况）",
         "kp": "剪拼探究",
         "tags": "图形,剪拼,探究"},
        {"unit": 6, "diff": 3, "section": "fill_blank",
         "content": "至少用（    ）个完全相同的小正方形可以拼成一个大正方形；至少用（    ）个完全相同的小正方体可以拼成一个大正方体。",
         "answer": "4；8",
         "kp": "拼组规律",
         "tags": "图形,拼组,规律"},
    ])

    for item in gfx:
        q = Question(
            unit=item["unit"],
            section=item.get("section", "fill_blank"),
            difficulty=item["diff"],
            content=item["content"],
            answer=item["answer"],
            options=item.get("options", ""),
            knowledge_point=item["kp"],
            tags=item.get("tags", ""),
        )
        # 图形题在 content 中包含渲染提示（以 JSON 形式存储在 tags 中）
        if "graphic" in item:
            import json
            q.tags = item["tags"] + ",graphic:" + json.dumps(item["graphic"], ensure_ascii=False)
        questions.append(q)

    return questions
