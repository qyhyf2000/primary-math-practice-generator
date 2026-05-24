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
        scrape_result = self._scrape_urls()
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

    def _scrape_urls(self, grade_filter: int = None, term_filter: int = None) -> dict:
        """从配置的URL学习题目结构并生成变形题（不再直接存储抓取内容）"""
        from .scrapers import learn_and_generate

        url_entries = []
        scraper_urls = self.sync_config.get("scraper_urls", [])
        for entry in scraper_urls:
            if isinstance(entry, dict):
                g = entry.get("grade", 2)
                t = entry.get("term", 2)
                if grade_filter and g != grade_filter:
                    continue
                if term_filter and t != term_filter:
                    continue
                url_entries.append((entry["url"], g, t))
            elif isinstance(entry, str):
                url_entries.append((entry, 2, 2))

        if not url_entries:
            return {"added": 0, "skipped": 0, "error": None}

        added = 0
        errors = []

        for url, g, t in url_entries:
            try:
                qs = learn_and_generate(url, grade=g, term=t, per_template=3)
                if qs:
                    cnt = self.db.insert_batch(qs)
                    added += cnt
                    logger.info(f"学习 {url[-40:]}: 生成 {len(qs)} 题, 入库 {cnt} 题")
            except Exception as e:
                errors.append(f"{url[-30:]}: {e}")
                continue

        err_msg = "; ".join(errors[:3]) if errors else None
        return {"added": added, "skipped": 0, "error": err_msg}

    # ================================================================
    # 来源3：远程 API
    # ================================================================

    def _fetch_from_api(self, api_url: str) -> dict:
        """从远程 API 获取题目"""
        try:
            import requests
            headers = {}
            api_key = self.sync_config.get("api_key", "")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            resp = requests.get(api_url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return self._process_remote_questions(data)
        except ImportError:
            logger.warning("requests 未安装，无法访问远程 API")
            return {"added": 0, "skipped": 0, "error": "requests 未安装"}
        except Exception as e:
            logger.warning(f"API 请求失败: {e}")
            return {"added": 0, "skipped": 0, "error": str(e)}

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
