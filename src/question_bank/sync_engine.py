"""
题库自动更新引擎

支持三种更新来源：
1. 本地算法生成 — 最可靠，自动生成新题
2. 网络抓取 — 从免费教育网站抓取题目
3. 远程 API — 对接第三方题库 API（待接入）
"""
import hashlib
import json
import logging
import random
from typing import List, Optional
from datetime import datetime

import requests

from .db_manager import DBManager
from .models import Question
from .question_generator import generate_questions

logger = logging.getLogger(__name__)


class SyncEngine:
    def __init__(self, db: DBManager, sync_config: dict):
        self.db = db
        self.sync_config = sync_config
        self._scheduler = None

    @property
    def is_enabled(self) -> bool:
        return self.sync_config.get("enabled", False)

    # ================================================================
    # 主入口：一键更新
    # ================================================================

    def sync_once(self) -> dict:
        """
        执行一次完整更新。依次尝试：
        1. 算法生成新题
        2. 网络抓取（如果配置了URL）
        3. 本地文件导入（如果 data/import/ 下有文件）
        """
        if not self.is_enabled and not self.sync_config.get("generator_enabled", True):
            return {"generated": 0, "scraped": 0, "imported": 0,
                    "error": "同步未启用（config.yaml 中 sync.enabled: false）"}

        result = {"generated": 0, "scraped": 0, "imported": 0, "error": None}

        # 1. 算法生成
        gen_count = self.sync_config.get("generator_count", 20)
        gen_result = self._generate_questions(gen_count)
        result["generated"] = gen_result["added"]
        if gen_result.get("error"):
            result["error"] = gen_result["error"]

        # 2. 网络抓取
        scraper_url = self.sync_config.get("scraper_url", "")
        if scraper_url:
            scrape_result = self._scrape_from_web(scraper_url)
            result["scraped"] = scrape_result["added"]
            if scrape_result.get("error") and not result["error"]:
                result["error"] = scrape_result["error"]

        # 3. 远程 API
        api_url = self.sync_config.get("url", "")
        if api_url:
            api_result = self._fetch_from_api(api_url)
            result["scraped"] += api_result["added"]
            if api_result.get("error") and not result["error"]:
                result["error"] = api_result["error"]

        # 4. 本地导入
        import_result = self._import_local_files()
        result["imported"] = import_result["added"]

        total = result["generated"] + result["scraped"] + result["imported"]
        logger.info(f"同步完成: 生成{result['generated']}, 抓取{result['scraped']}, "
                     f"导入{result['imported']}, 共新增{total}题")
        return result

    # ================================================================
    # 来源1：算法生成
    # ================================================================

    def _generate_questions(self, count: int) -> dict:
        """用算法生成新题目并入库"""
        try:
            qs = generate_questions(count=count)
            added = 0
            skipped = 0
            for q in qs:
                if self.db.content_exists(q.content):
                    skipped += 1
                    continue
                self.db.insert_question(q)
                added += 1
            return {"added": added, "skipped": skipped, "error": None}
        except Exception as e:
            logger.error(f"算法生成失败: {e}")
            return {"added": 0, "skipped": 0, "error": str(e)}

    # ================================================================
    # 来源2：网络抓取
    # ================================================================

    def _scrape_from_web(self, url: str) -> dict:
        """
        从免费教育网站抓取题目。

        支持的模式：
        - url 是具体 JSON API 地址时，直接请求解析
        - url 为空时跳过
        """
        if not url:
            return {"added": 0, "skipped": 0, "error": None}

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36"
            }
            api_key = self.sync_config.get("api_key", "")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()

            # 尝试 JSON
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type:
                data = resp.json()
                return self._process_remote_questions(data)
            else:
                # HTML 页面 — 尝试提取题目
                return self._scrape_html(resp.text)
        except requests.RequestException as e:
            logger.warning(f"网络抓取失败: {e}")
            return {"added": 0, "skipped": 0, "error": str(e)}

    def _scrape_html(self, html: str) -> dict:
        """
        从 HTML 页面中提取数学题。

        针对常见题库站点的页面结构做简单解析。
        对于复杂的反爬页面，此方法可能无法正常工作，
        但不会阻塞其他更新来源。

        支持的简单模式：
        - <div class="question"> 或 <p class="timu">
        - 纯文本行中包含 "÷ × + - =" 运算符号的行
        """
        added = 0
        skipped = 0

        try:
            from html.parser import HTMLParser

            class QuestionParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.questions = []
                    self.in_question = False
                    self.current = ""

                def handle_starttag(self, tag, attrs):
                    attrs_dict = dict(attrs)
                    cls = attrs_dict.get("class", "")
                    if "question" in cls.lower() or "timu" in cls.lower():
                        self.in_question = True
                        self.current = ""

                def handle_endtag(self, tag):
                    if self.in_question and tag in ("div", "p", "li"):
                        self.in_question = False
                        text = self.current.strip()
                        if text and any(op in text for op in "÷×+-="):
                            self.questions.append(text)

                def handle_data(self, data):
                    if self.in_question:
                        self.current += data

            parser = QuestionParser()
            parser.feed(html)

            for text in parser.questions[:50]:
                if self.db.content_exists(text):
                    skipped += 1
                    continue
                # 简单题目：无法确定unit/section时标记为待分类
                q = Question(
                    unit=0, section="oral_calc", difficulty=1,
                    content=text, answer="", source="scraped",
                    tags="待审核",
                )
                self.db.insert_question(q)
                added += 1

        except Exception as e:
            logger.warning(f"HTML解析失败: {e}")

        return {"added": added, "skipped": skipped, "error": None}

    # ================================================================
    # 来源3：远程 API
    # ================================================================

    def _fetch_from_api(self, url: str) -> dict:
        """从远程 API 获取题目"""
        return self._scrape_from_web(url)  # 复用抓取逻辑

    def _process_remote_questions(self, data) -> dict:
        """处理远程返回的题目数据"""
        if not isinstance(data, list):
            return {"added": 0, "skipped": 0, "error": "API返回格式错误"}

        added = 0
        skipped = 0
        for item in data:
            required = ["content", "answer"]
            if not all(k in item for k in required):
                skipped += 1
                continue
            if self.db.content_exists(item["content"]):
                skipped += 1
                continue
            q = Question(
                unit=item.get("unit", 0),
                section=item.get("section", "oral_calc"),
                difficulty=item.get("difficulty", 1),
                content=item["content"],
                answer=item["answer"],
                options=item.get("options", ""),
                knowledge_point=item.get("knowledge_point", ""),
                tags=item.get("tags", ""),
                source="sync",
            )
            self.db.insert_question(q)
            added += 1

        return {"added": added, "skipped": skipped, "error": None}

    # ================================================================
    # 来源4：本地文件导入
    # ================================================================

    def _import_local_files(self) -> dict:
        """
        从 data/import/ 目录导入题目文件。

        支持格式：
        - .json: [{"content": "...", "answer": "...", ...}, ...]
        - .jsonl: 每行一个 JSON 对象
        - .yaml: 题目列表
        """
        import os
        from pathlib import Path

        import_dir = Path(self.db.db_path).parent / "import"
        if not import_dir.exists():
            return {"added": 0, "error": None}

        added = 0
        for f in import_dir.glob("*"):
            try:
                if f.suffix == ".json":
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    if isinstance(data, list):
                        result = self._process_remote_questions(data)
                        added += result["added"]

                elif f.suffix in (".yaml", ".yml"):
                    import yaml
                    with open(f, "r", encoding="utf-8") as fp:
                        data = yaml.safe_load(fp)
                    if isinstance(data, list):
                        result = self._process_remote_questions(data)
                        added += result["added"]
            except Exception as e:
                logger.warning(f"导入文件 {f.name} 失败: {e}")

        return {"added": added, "error": None}

    # ================================================================
    # 定时调度
    # ================================================================

    def start_scheduler(self):
        """启动定时自动更新"""
        if not self.is_enabled:
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            self._scheduler = BackgroundScheduler()
            hours = self.sync_config.get("interval_hours", 168)
            self._scheduler.add_job(
                self.sync_once,
                "interval",
                hours=hours,
                id="question_bank_sync",
                replace_existing=True,
            )
            self._scheduler.start()
            logger.info(f"定时更新已启动（每{hours}小时）")
        except ImportError:
            logger.warning("APScheduler未安装，跳过定时调度")

    def stop_scheduler(self):
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
