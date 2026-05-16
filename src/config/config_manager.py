"""配置管理器 - 加载和验证 YAML 配置文件"""
import os
import yaml
from pathlib import Path


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)
        self._validate()

    def _validate(self):
        required = ["grade", "exam", "question_bank", "rendering"]
        for key in required:
            if key not in self._data:
                raise ValueError(f"配置文件缺少必需字段: {key}")

        grade = self._data["grade"]
        for k in ["name", "term", "textbook"]:
            if k not in grade:
                raise ValueError(f"grade.{k} 为必填项")

        sections = self._data["exam"].get("sections", [])
        if not sections:
            raise ValueError("exam.sections 至少需要一个题型配置")

        for sec in sections:
            for k in ["id", "title", "count", "score_per_question", "difficulty_range"]:
                if k not in sec:
                    raise ValueError(f"题型配置缺少字段: {k}")

    @property
    def data(self):
        return self._data

    @property
    def grade_name(self):
        return self._data["grade"]["name"]

    @property
    def grade_term(self):
        return self._data["grade"]["term"]

    @property
    def textbook(self):
        return self._data["grade"]["textbook"]

    def get_sections(self):
        return self._data["exam"]["sections"]

    def get_db_path(self):
        db_rel = self._data["question_bank"]["db_path"]
        return str(Path(__file__).parent.parent.parent / db_rel)

    def get_output_dir(self):
        output_dir = Path(__file__).parent.parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)

    def get_seed_on_empty(self):
        return self._data["question_bank"].get("seed_on_empty", True)

    def get_dedup_window_weeks(self):
        return self._data["question_bank"].get("dedup_window_weeks", 4)

    def get_sync_config(self):
        return self._data["question_bank"].get("sync", {})

    def get_rendering_config(self):
        return self._data["rendering"]

    def exam_title(self, week_label: str = "") -> str:
        template = self._data["exam"]["title_template"]
        title = template.format(
            textbook=self.textbook,
            grade=self.grade_name,
            term=self.grade_term,
            week=week_label
        )
        return title
