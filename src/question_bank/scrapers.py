"""
网络抓取器 — 从免费教育网站抓取小学数学题

支持的站点:
- 无忧考网 (51test.net) — 主要来源，公开可访问
- 瑞文网 (ruiwen.com) — 教育资料站
- 通用数学表达式提取 — 任意 HTML 页面兜底
"""
import re
import json
import time
import random
import logging
from typing import List, Optional, Dict
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import Question

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 二年级数学题常见模式
MATH_PATTERNS = [
    (re.compile(r'(\d+)\s*([÷×+\-])\s*(\d+)\s*=\s*(?:(\d+)(?:\.\.\.(\d+))?)?'), "oral_calc"),
    (re.compile(r'\((\d+)\s*([+\-])\s*(\d+)\)\s*([÷×])\s*(\d+)'), "oral_calc"),
    (re.compile(r'.*?[（(]\s*[）)]\s*.*'), "fill_blank"),
    (re.compile(r'^\s*(\d{2,4})\s*$\s*^\s*([+\-])\s*(\d{2,4})\s*$', re.MULTILINE), "vertical_calc"),
    (re.compile(r'.*?(?:多少|几个|一共|还剩|应付|找回|平均).*?[？?]'), "word_problem"),
    (re.compile(r'.*?[○Oo].*?'), "fill_blank"),
    (re.compile(r'.*?(?:时|分|秒|千米|米|分米|厘米|毫米).*?[=(（].*?[)）]?'), "fill_blank"),
]


def _create_session() -> requests.Session:
    """创建带重试机制的会话"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session


def fetch_page(url: str, timeout: int = 20) -> str:
    """获取网页 HTML 文本，自动处理编码（含重试）"""
    session = _create_session()
    resp = session.get(url, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()

    if resp.encoding == "ISO-8859-1" or resp.apparent_encoding != resp.encoding:
        resp.encoding = resp.apparent_encoding

    text = resp.text
    if "�" in text or "\\x" in repr(text[:100]):
        for enc in ["gb2312", "gbk", "utf-8"]:
            try:
                text = resp.content.decode(enc)
                if any(kw in text for kw in ["数学", "口算", "年级", "计算"]):
                    break
            except Exception:
                continue
    return text


def _clean_html(text: str) -> str:
    """清理 HTML 标签和实体"""
    # 替换常见标签为换行
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</?p[^>]*>', '\n', text)
    text = re.sub(r'</?div[^>]*>', '\n', text)
    text = re.sub(r'<li[^>]*>', '\n· ', text)
    text = re.sub(r'</li>', '', text)
    # 移除其他标签
    text = re.sub(r'<[^>]+>', '', text)
    # 替换 HTML 实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#169;', '')  # copyright
    # 压缩多余空白
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


# ============================================================
# 站点专用抓取器
# ============================================================

def scrape_51test(url: str) -> List[Dict]:
    """
    抓取无忧考网 (51test.net) 页面。

    该站点题目通常位于 <div class="content-txt" id="content-txt"> 内，
    答案可能在:
    - 同一 div 内每道题后的括号或（　）中
    - 页面底部单独的答案区域（如 "参考答案" 段落）
    - 答案在 <span style="color:red"> 或其他颜色标记中
    """
    text = fetch_page(url)

    # 提取 content-txt 区域
    content_match = re.search(
        r'<div[^>]*id=["\']content-txt["\'][^>]*>(.*?)</div>\s*(?:<div|<!--)',
        text, re.DOTALL
    )
    if not content_match:
        content_match = re.search(
            r'id=["\']content-txt["\'][^>]*>(.*?)</div>',
            text, re.DOTALL
        )
    if not content_match:
        logger.warning(f"未在页面中找到 content-txt 区域: {url}")
        return []

    content_html = content_match.group(1)

    # 尝试提取答案区域（通常单独在一个 div 或段落中）
    answer_text = _extract_answer_section(content_html)

    content = _clean_html(content_html)
    return _parse_math_content(content, source_url=url, answer_text=answer_text)


def scrape_ruiwen(url: str) -> List[Dict]:
    """
    抓取瑞文网 (ruiwen.com) 页面。

    该站点内容通常在 <div class="content"> 或 <article> 中。
    """
    text = fetch_page(url)

    # 提取正文区域
    content_match = re.search(
        r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>\s*(?:<div|<!--)',
        text, re.DOTALL
    )
    if not content_match:
        content_match = re.search(
            r'<article[^>]*>(.*?)</article>',
            text, re.DOTALL
        )
    if not content_match:
        content_match = re.search(
            r'<div[^>]*class=["\'][^"\']*article[^"\']*["\'][^>]*>(.*?)</div>',
            text, re.DOTALL
        )

    if content_match:
        content_html = content_match.group(1)
        answer_text = _extract_answer_section(content_html)
        content = _clean_html(content_html)
        return _parse_math_content(content, source_url=url, answer_text=answer_text)
    else:
        # 回退到全页面解析
        content = _clean_html(text)
        return _parse_math_content(content, source_url=url)


def scrape_generic(url: str) -> List[Dict]:
    """通用抓取：提取任意页面中的数学表达式"""
    text = fetch_page(url)
    cleaned = _clean_html(text)
    return _parse_math_content(cleaned, source_url=url)


def _extract_answer_section(html: str) -> Optional[str]:
    """
    从 HTML 中提取独立的答案区域。

    常见模式：
    - "参考答案"、"答案" 后面的内容
    - 用颜色标记的答案（如 red, blue）
    - 页面底部的答案列表
    """
    answer_text = ""

    # 模式1：参考答案标题后的内容
    ans_patterns = [
        # 匹配 "参考答案" 之后直到下一个章节标题或结束的所有内容
        r'(?:参考[答案解答]|答案)[：:\s]*</[^>]*>\s*(.+?)(?=<(?:div|h[1-6]|p)[^>]*>\s*(?:[一二三四五六七八九]|\d+[\.、]|$|</div))',
        r'(?:参考[答案解答]|答案)[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九])|$)',
    ]

    for pat in ans_patterns:
        matches = re.findall(pat, html, re.DOTALL | re.IGNORECASE)
        if matches:
            for m in matches:
                cleaned = _clean_html(m).strip()
                if len(cleaned) > 5:
                    answer_text += cleaned + "\n"
            if answer_text.strip():
                break

    # 如果以上都未匹配，尝试查找 "答案" 后一整段直到页面底部的文本
    if not answer_text.strip():
        m = re.search(
            r'(?:参考[答案解答]|答案)\s*(?:</[^>]+>\s*)*[：:\s]*\s*(.+?)(?=\s*(?:<div[^>]*class=["\'](?:page|footer|related|comment)|\Z))',
            html, re.DOTALL | re.IGNORECASE
        )
        if m:
            cleaned = _clean_html(m.group(1)).strip()
            if len(cleaned) > 5:
                answer_text = cleaned

    # 模式2：查找 span/font 中有颜色标记的答案
    if not answer_text:
        color_matches = re.findall(
            r'<(?:span|font)[^>]*color\s*=\s*["\']?(?:red|#ff0000|blue|#0000ff)[^"\']*["\']?[^>]*>(.*?)</(?:span|font)>',
            html, re.DOTALL | re.IGNORECASE
        )
        if color_matches:
            answer_text = " ".join(m.strip() for m in color_matches if len(m.strip()) > 1)

    return answer_text if answer_text else None


def _parse_answer_list(answer_text: str) -> Dict[int, str]:
    """
    将答案文本解析为 题号->答案 的映射。

    支持格式：
    - "1.A 2.B 3.C" (选择题答案)
    - "1. 钝角 2. 锐角 3. 直角" (填空题答案)
    - "一、1. 240 2. 5...3" (带序号)
    """
    answer_map = {}
    # 匹配 "数字. 答案内容" 的模式
    items = re.findall(r'(\d+)\s*[\.、．]\s*([^；;，,\d]{1,30}?)(?=\s*\d+\s*[\.、．]|\s*$)', answer_text)
    for num, ans in items:
        answer_map[int(num)] = ans.strip()
    return answer_map


# ============================================================
# 内容解析
# ============================================================

def _parse_math_content(text: str, source_url: str = "",
                        answer_text: str = None) -> List[Dict]:
    """
    从纯文本中解析出数学题。
    策略：按题号切分文本，每个片段尝试分类。
    如果有独立的答案文本，尝试匹配到各题。
    """
    questions = []

    # 解析独立答案区域
    answer_map = {}
    if answer_text:
        answer_map = _parse_answer_list(answer_text)

    # 移除章节标题前缀
    text = re.sub(r'[一二三四五六七八九]、[^。\n]{2,30}[。)】]\s*(?:（[^）]*）)?', '', text)

    # 剥离【答案】... 和【解析】... 等答案块
    text = re.sub(r'[【\[]答案[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]解析[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]来源[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]考点[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]详解[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]参考答案[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|答案与|参考答案)|$)', '', text, flags=re.DOTALL)

    # 按题号切分文本
    parts = re.split(r'(\d+)\s*[.\．]', text)

    i = 0
    question_index = 0

    # 处理第一个非数字片段
    if parts and not parts[0].strip().isdigit():
        first = parts[0].strip()
        if len(first) > 5:
            question_index += 1
            q = _classify_and_create(first, source_url,
                                     answer_map.get(question_index, ""))
            if q:
                questions.append(q)
        i = 1

    while i + 1 < len(parts):
        num = parts[i].strip()
        content = parts[i + 1].strip()
        if num.isdigit() and content:
            question_index += 1
            combined = f'{num}. {content}'
            q = _classify_and_create(combined, source_url,
                                     answer_map.get(question_index, ""))
            if q:
                questions.append(q)
        i += 2

    if i < len(parts):
        rest = parts[i].strip()
        if len(rest) > 5:
            question_index += 1
            q = _classify_and_create(rest, source_url,
                                     answer_map.get(question_index, ""))
            if q:
                questions.append(q)

    return questions


# 非数学题内容黑名单（教育网站介绍文字）
_NON_QUESTION_KEYWORDS = [
    "无忧考网", "为大家整理", "希望对大家", "版权所有", "免责声明",
    "来源", "推荐文章", "相关文章", "更多试题", "本页导航", "返回目录",
    "点击下载", "下一页", "上一页", "答题卡", "试卷结构", "分页",
    "版权声明", "未经许可", "转载", "打印本页", "关闭窗口",
    "练习题及答案", "篇一", "篇二", "篇三", "小学二年级下册",
    "及答案（数学）", "【答案】", "【解析】", "参考答案",
]

# 数学题特征（白名单信号）
_MATH_SIGNAL_KEYWORDS = [
    "多少", "几个", "一共", "还剩", "应付", "找回", "平均", "最多",
    "至少", "每份", "总共", "计算", "口算", "竖式", "脱式",
    "除法", "乘法", "加法", "减法", "被除数", "除数", "商", "余数",
    "混合运算", "读作", "写作", "组成", "数位", "读数", "写数",
    "个", "米", "厘米", "分米", "毫米", "千米", "元", "角", "分",
    "时", "秒", "克", "千克", "本", "支", "张", "条", "件",
    "连线", "画一画", "量一量", "比一比", "数一数",
    "长方形", "正方形", "平行四边形", "三角形", "直角", "锐角", "钝角",
    "统计", "调查", "记录", "钟面", "时针", "分针",
]


def _is_valid_math_question(text: str) -> bool:
    """
    判断一段文本是否可能是数学题。

    两级过滤：
    - 黑名单：包含教育网站介绍特征词 → 直接拒绝
    - 白名单：包含任一数学特征信号 → 接受
    """
    if len(text) < 5:
        return False

    # Stage A：黑名单
    for kw in _NON_QUESTION_KEYWORDS:
        if kw in text:
            return False

    # 排除分数/题量标注：如 "（共26分）" "（共5题）" "分值：共26分"
    if re.search(r'[（(]共\s*\d+\s*(?:分|题)', text):
        stripped = re.sub(r'[（(]共[^）)]*[）)]', '', text).strip()
        if len(stripped) < 8:
            return False
    if re.search(r'(?:分值|满分|总分)\s*[：:]\s*共?\s*\d+\s*(?:分|题)', text):
        stripped = re.sub(r'(?:分值|满分|总分)\s*[：:]\s*共?\s*\d+\s*(?:分|题)', '', text).strip()
        if len(stripped) < 8:
            return False

    # Stage B：白名单
    # 1. 数学运算符
    if re.search(r'[÷×+\-=]', text):
        return True

    # 2. 空括号填空标记
    if re.search(r'[（(]\s*[）)]', text):
        return True
    if "___" in text or "____" in text or "○" in text:
        return True

    # 3. 问句 + 数学关键词
    if ("？" in text or "?" in text) and any(
        kw in text for kw in ["多少", "几个", "一共", "还剩", "应付", "找回",
                               "平均", "最多", "至少", "总共", "租"]
    ):
        return True

    # 4. 数字 + 量词
    if re.search(r'\d+\s*(?:个|米|厘米|分米|毫米|千米|元|角|分|时|秒|克|千克|本|支|张|条|件|次|倍|人|天|岁|只|头|棵|朵|颗|片|辆|周|页|题)', text):
        return True

    # 5. 数学概念关键词
    if any(kw in text for kw in _MATH_SIGNAL_KEYWORDS):
        return True

    return False


# 答案/解析污染模式
_ANSWER_PATTERNS = [
    re.compile(r'[【\[]答案[】\]].*', re.DOTALL),
    re.compile(r'[【\[]解答[】\]].*', re.DOTALL),
    re.compile(r'[【\[]解析[】\]].*', re.DOTALL),
    re.compile(r'[【\[]分析[】\]].*', re.DOTALL),
    re.compile(r'[【\[]来源[】\]].*', re.DOTALL),
    re.compile(r'[【\[]考点[】\]].*', re.DOTALL),
    re.compile(r'[【\[]详解[】\]].*', re.DOTALL),
    re.compile(r'[【\[]参考答案[】\]].*', re.DOTALL),
    re.compile(r'参考[答案解答]：.*', re.DOTALL),
    re.compile(r'答案[：:].*', re.DOTALL),
    re.compile(r'解[：:][\s\S]*', re.DOTALL),
    re.compile(r'分析[：:][\s\S]*', re.DOTALL),
    re.compile(r'(?:答案与解析|答案和解析)[\s\S]*', re.DOTALL),
]

# 非题目内容黑名单
_IMPURITY_KEYWORDS = [
    "参考答案", "答案与解析", "试题分析", "考点分析",
    "解题思路", "方法点拨", "题目解析", "答案解析",
    "篇十", "篇十一", "篇十二", "篇十三", "篇十四", "篇十五",
    "北师大版", "小学数学", "练习题及答案", "单元测试",
    "一、填空", "二、选择", "三、判断", "四、计算", "五、应用",
]


def _strip_answer_content(text: str) -> str:
    """移除答案、解析等非题目内容"""
    for pat in _ANSWER_PATTERNS:
        text = pat.sub('', text)
    return text.strip()


def _has_impurity(text: str) -> bool:
    """检测是否含非题目杂质"""
    # 含多个题号标记（如 "1. ... 2. ..."）→ 未正确拆分
    if len(re.findall(r'\d+[\.\、．）\)]\s*[A-Z一-鿿]', text)) > 1:
        return True
    # 含杂质关键词
    for kw in _IMPURITY_KEYWORDS:
        if kw in text:
            return True
    # 含大量 HTML 实体
    if text.count("&") >= 3:
        return True
    # 超长内容多半混了答案
    if len(text) > 200:
        return True
    # 含连续下划线（非填空，是HTML残留）
    if "________" in text or "_______" in text:
        return True
    return False


def _classify_and_create(text: str, source_url: str = "",
                         extracted_answer: str = "") -> Optional[Dict]:
    """分类一行文本并创建题目字典"""
    text = _strip_answer_content(text.strip())
    if len(text) < 3 or len(text) > 200:
        return None

    if _has_impurity(text):
        return None

    if not _is_valid_math_question(text):
        return None

    section = "oral_calc"
    difficulty = 1
    tags = []

    # -- 应用题特征 --
    if any(kw in text for kw in ["多少", "几个", "一共", "还剩", "应付", "找回", "平均", "租", "最多", "至少"]):
        if "?" in text or "？" in text or len(text) > 20:
            section = "word_problem"
            difficulty = 3
            tags.append("应用")

    # -- 竖式/脱式特征 --
    elif "竖式" in text or "用竖式计算" in text:
        section = "vertical_calc"
        difficulty = 2
        tags.append("竖式")
    elif "脱式" in text or "混合运算" in text:
        section = "vertical_calc"
        difficulty = 3
        tags.append("脱式")

    # -- 填空特征 --
    elif re.search(r'[（(]\s*[）)]', text):
        section = "fill_blank"
        difficulty = 1
    elif "___" in text or "____" in text:
        section = "fill_blank"
        difficulty = 2

    # -- 选择特征 --
    elif re.match(r'.*[A-D]\s*[\.\、]', text):
        section = "choice"
        difficulty = 2
        tags.append("选择")

    # -- 比较特征 --
    elif "○" in text:
        section = "fill_blank"
        difficulty = 1

    # -- 图形/几何特征 --
    if any(kw in text for kw in ["角", "直角", "锐角", "钝角", "长方形", "正方形",
                                   "平行四边形", "七巧板", "正方体", "立方体"]):
        if any(kw in text for kw in ["几个角", "几个直角", "数一数", "多少个"]):
            tags.append("图形")
            if section == "oral_calc":
                section = "fill_blank"
        elif any(kw in text for kw in ["画", "拼", "剪"]):
            tags.append("图形")

    # 无明确运算符时，进一步推断
    if section == "oral_calc" and not re.search(r'[\d]+\s*[÷×+\-]\s*[\d]+', text):
        if any(kw in text for kw in ["时", "分", "秒", "钟"]):
            section = "fill_blank"
            if "钟面" in text or "时针" in text or "分针" in text:
                tags.append("钟面")
        elif any(kw in text for kw in ["米", "厘米", "千米", "分米", "毫米"]):
            section = "fill_blank"
        elif any(kw in text for kw in ["千", "万", "读作", "写作", "组成"]):
            section = "fill_blank"
        elif any(kw in text for kw in ["角", "直角", "锐角", "钝角", "长方形", "正方形",
                                         "平行四边形", "七巧板"]):
            section = "fill_blank"
            tags.append("图形")
        elif "○" in text or ">" in text or "<" in text:
            section = "fill_blank"
        elif "连线" in text or "画一画" in text or "量" in text:
            section = "fill_blank"
        elif (re.search(r'\d', text) and len(text) > 8 and
              (bool(re.search(r'[÷×+\-=<>]', text)) or
               any(kw in text for kw in [
                   "多少", "几个", "一共", "还剩", "计算", "口算", "竖式",
                   "填空", "选择", "脱式", "个", "米", "厘米", "元", "角",
                   "÷", "×", "时", "分", "秒", "除法", "乘法",
               ]))):
            section = "fill_blank"
        else:
            return None

    # 推断单元
    unit = _infer_unit(text)

    # 提取答案：优先用外部传入的答案，其次从题目文本中提取
    answer = extracted_answer if extracted_answer else ""
    if not answer:
        # 匹配全角括号: （xxxxx）
        m = re.search(r'（([^）]{1,50}?)）', text)
        if m:
            candidate = m.group(1).strip()
            if candidate and len(candidate) < 50:
                answer = candidate
    if not answer:
        # 匹配半角括号: (xxxxx)
        m = re.search(r'\(([^)]{1,30})\)', text)
        if m:
            candidate = m.group(1).strip()
            if candidate and len(candidate) < 30:
                answer = candidate

    # 将 content 中的括号答案替换为空括号，防止答案泄露到试卷上
    if answer:
        text = re.sub(r'（[^）]{1,50}）', '（    ）', text)
        text = re.sub(r'\([^)]{1,30}\)', '(    )', text)

    # 剥离【答案】... 【解析】... 【来源】... 块
    text = re.sub(r'[【\[]答案[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|参考答案|答案与)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]解析[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|参考答案|答案与)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]来源[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|参考答案|答案与)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]考点[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|参考答案|答案与)|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[【\[]参考答案[】\]].*?(?=[【\[]\s*(?:答案|解析|来源|考点|详解|参考答案|答案与)|$)', '', text, flags=re.DOTALL)

    # 组装标签
    tag_str = ",".join(tags) if tags else ""

    return {
        "content": text[:200],
        "answer": answer or "(待补充)",
        "section": section,
        "difficulty": difficulty,
        "unit": unit,
        "source_url": source_url,
        "tags": tag_str,
    }


def _infer_unit(text: str) -> int:
    """根据文本内容推断所属单元"""
    if any(kw in text for kw in ["除", "÷", "余", "租", "最多", "至少"]):
        return 1
    if any(kw in text for kw in ["括号", "先乘", "先算", "后算", "脱式"]):
        return 2
    if any(kw in text for kw in ["千", "万", "读作", "写作", "组成", "数位"]):
        return 3
    if any(kw in text for kw in ["千米", "米", "分米", "厘米", "毫米", "km", "m", "cm", "mm"]):
        return 4
    if any(kw in text for kw in ["加", "减", "进位", "退位", "验算", "+", "-"]):
        if any(kw in text for kw in ["百", "三位"]):
            return 5
    if any(kw in text for kw in ["角", "直角", "锐角", "钝角", "长方形", "正方形", "平行四边形",
                                   "七巧板", "正方体", "立方体"]):
        return 6
    if any(kw in text for kw in ["时", "分", "秒", "钟", "时间"]):
        return 7
    if any(kw in text for kw in ["统计", "调查", "正字", "记录"]):
        return 8
    # 通用计算题归到混合运算
    if re.search(r'[\d]+\s*[÷×]\s*[\d]+', text):
        return 2
    if re.search(r'[\d]{2,}\s*[+\-]\s*[\d]{2,}', text):
        return 5
    return 0


# ============================================================
# 批量抓取入口
# ============================================================

KNOWN_51TEST_URLS = [
    "https://www.51test.net/show/2968915.html",
    "https://www.51test.net/show/11231919.html",
    "https://www.51test.net/show/9699960.html",
]

# 瑞文网二年级数学题页面（公开可访问）
KNOWN_RUIWEN_URLS = [
    "https://www.ruiwen.com/shiti/ernianjishuxue.html",
]


def scrape_urls(urls: List[str]) -> List[Dict]:
    """
    批量抓取 URL 列表。

    自动识别站点并调用对应的抓取器。
    返回题目字典列表。
    """
    all_questions = []
    for url in urls:
        if not url or not url.startswith("http"):
            continue
        try:
            domain = urlparse(url).netloc.lower()
            if "51test.net" in domain:
                qs = scrape_51test(url)
            elif "ruiwen.com" in domain:
                qs = scrape_ruiwen(url)
            else:
                qs = scrape_generic(url)
            all_questions.extend(qs)
            logger.info(f"从 {url[:60]} 抓取到 {len(qs)} 题")
        except requests.ConnectionError as e:
            logger.warning(f"连接 {url[:60]} 失败（网络不可达）: {e}")
        except requests.Timeout:
            logger.warning(f"连接 {url[:60]} 超时")
        except requests.HTTPError as e:
            logger.warning(f"HTTP 错误 {e.response.status_code if e.response else '?'}: {url[:60]}")
        except Exception as e:
            logger.error(f"解析 {url[:60]} 出错: {e}")
    return all_questions


def quick_test_scrape(url: str) -> dict:
    """
    快速测试单个 URL 的抓取效果，返回诊断信息。

    用于调试和评估抓取质量。
    """
    result = {
        "url": url,
        "status": "unknown",
        "questions_found": 0,
        "sample": [],
        "error": None,
    }
    try:
        text = fetch_page(url)
        result["status"] = f"fetched {len(text)} chars"
        domain = urlparse(url).netloc.lower()
        if "51test.net" in domain:
            qs = scrape_51test(url)
        elif "ruiwen.com" in domain:
            qs = scrape_ruiwen(url)
        else:
            qs = scrape_generic(url)
        result["questions_found"] = len(qs)
        result["sample"] = [
            {"content": q["content"][:80], "section": q["section"],
             "answer": q["answer"][:30], "unit": q["unit"]}
            for q in qs[:5]
        ]
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result


# ============================================================
# 模板提取 + 变形生成（从网页学习题目结构，生成变体）
# ============================================================

def extract_template(text: str) -> Optional[Dict]:
    """
    从一段题目文本中提取可参数化的模板。

    识别文本中的数字并替换为占位符，保留语言结构。
    返回 {"template": str, "params": dict, "answer_template": str}
    或 None（文本不适合做模板）。
    """
    text = _strip_answer_content(text.strip())
    if len(text) < 8 or len(text) > 150:
        return None
    if not _is_valid_math_question(text):
        return None

    # 将数字替换为参数占位符 {n0}, {n1}, ...
    params = {}
    counter = [0]

    def replace_num(m):
        val = int(m.group())
        key = f"n{counter[0]}"
        params[key] = val
        counter[0] += 1
        return f"{{{key}}}"

    # 只替换独立的数字（不在中文词中的）
    template = re.sub(r'(?<![一-鿿\d])\d+(?![一-鿿\d\.\d])', replace_num, text)

    # 至少要有 1 个数字参数
    if not params:
        return None

    return {
        "template": template,
        "params": params,
        "original": text,
    }


def _safe_randint(lo: int, hi: int) -> int:
    """安全随机整数，lo > hi 时自动交换或返回 lo"""
    if lo > hi:
        lo, hi = hi, lo
    if lo == hi:
        return lo
    return random.randint(lo, hi)


def generate_variation(template_info: Dict, grade: int = 2, term: int = 2) -> Optional[str]:
    """
    基于模板生成一个变形题（替换数字参数）。

    根据年级调整参数范围：
      G1-G2: 数字范围 1-20
      G3-G4: 数字范围 1-999
      G5-G6: 数字范围 1-9999，可含小数
    """
    tpl = template_info["template"]
    params = template_info["params"]

    if grade <= 2:
        new_params = {k: _safe_randint(1, max(1, min(20, v * 2)))
                      for k, v in params.items()}
    elif grade <= 4:
        new_params = {k: _safe_randint(max(1, v // 2), max(2, min(999, v * 2)))
                      for k, v in params.items()}
    else:
        new_params = {}
        for k, v in params.items():
            lo = max(1, v // 2)
            hi = max(2, min(9999, v * 2))
            if random.random() < 0.3:
                new_params[k] = round(random.uniform(float(lo), float(hi)), 1)
            else:
                new_params[k] = _safe_randint(lo, hi)

    try:
        return tpl.format(**new_params)
    except (KeyError, ValueError):
        return None


def scrape_templates(url: str) -> List[Dict]:
    """
    从 URL 抓取并提取题目模板（不取答案，只学结构）。

    返回模板列表，每个含 template/preview/grade 信息。
    """
    text = fetch_page(url)
    cleaned = _clean_html(text)

    # 按行分割，每行尝试提取模板
    lines = cleaned.split('\n')
    templates = []
    seen = set()

    for line in lines:
        line = line.strip()
        if len(line) < 8:
            continue

        tmpl = extract_template(line)
        if tmpl and tmpl["template"] not in seen:
            seen.add(tmpl["template"])
            templates.append(tmpl)

    return templates


def learn_and_generate(url: str, grade: int = 2, term: int = 2,
                       per_template: int = 3) -> List[Question]:
    """
    从 URL 学习题目结构，生成干净的变形题。

    流程：抓取页面 → 提取模板 → 每模板生成 N 个变体 → 返回 Question 列表。
    """
    text = fetch_page(url)
    cleaned = _clean_html(text)

    # 尝试分离答案区域
    answer_text = _extract_answer_section(text)
    if answer_text:
        # 有答案区域 → 尝试去掉答案后的纯题目部分
        main_content = text
        for tag in ['参考答案', '答案与解析', '答案解析']:
            idx = main_content.find(tag)
            if idx > 0:
                main_content = main_content[:idx]
                break
        cleaned = _clean_html(main_content)

    lines = cleaned.split('\n')
    templates = []
    seen = set()

    for line in lines:
        tmpl = extract_template(line.strip())
        if tmpl and tmpl["template"] not in seen:
            seen.add(tmpl["template"])
            templates.append(tmpl)

    questions = []
    for tmpl in templates[:20]:
        for _ in range(per_template):
            try:
                content = generate_variation(tmpl, grade, term)
            except Exception:
                continue
            if content and _is_valid_math_question(content):
                # 根据内容判断题型
                section = "oral_calc"
                difficulty = 1
                if "?" in content or "？" in content or len(content) > 20:
                    section = "word_problem"
                    difficulty = 3
                elif re.search(r'[（(]\s*[）)]', content):
                    section = "fill_blank"
                    difficulty = 1

                q = Question(
                    grade=grade, term=term, unit=0,
                    section=section, difficulty=difficulty,
                    content=content, answer="",
                    knowledge_point="网络学习生成",
                    tags=f"learned,{url[-40:]}",
                    source="generated",
                )
                questions.append(q)

    return questions
