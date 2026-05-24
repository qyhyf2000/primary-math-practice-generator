"""配置管理器 - 加载和验证 YAML 配置文件，支持多年级切换"""
import yaml
from pathlib import Path
from typing import Optional


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            self._project_root = Path(__file__).parent.parent.parent
            config_path = self._project_root / "config.yaml"
        else:
            config_path = Path(config_path)
            self._project_root = config_path.parent

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"配置文件未找到: {config_path}\n请确保项目根目录下存在 config.yaml 文件"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误 ({config_path}):\n{e}")

        if self._data is None:
            raise ValueError(f"配置文件为空: {config_path}")

        # 当前激活的年级/学期
        active = self._data.get("active", {})
        self._active_grade = active.get("grade", 2)
        self._active_term = active.get("term", 2)

        self._validate()

    def _validate(self):
        required = ["curriculum", "exam", "question_bank", "rendering"]
        for key in required:
            if key not in self._data:
                raise ValueError(f"配置文件缺少必需字段: {key}")

        sections = self._data["exam"].get("sections", [])
        if not sections:
            raise ValueError("exam.sections 至少需要一个题型配置")

        for sec in sections:
            for k in ["id", "title", "count", "score_per_question", "difficulty_range"]:
                if k not in sec:
                    raise ValueError(f"题型配置缺少字段: {k}")

    # ================================================================
    # 年级/学期切换
    # ================================================================

    def set_active(self, grade: int, term: int):
        """切换当前年级/学期，影响 get_units/exam_title 等方法的返回值"""
        key = f"{grade}-{term}"
        if key not in self._data.get("curriculum", {}):
            raise ValueError(f"不支持的年级/学期: {key}")
        self._active_grade = grade
        self._active_term = term

    @property
    def active_grade(self) -> int:
        return self._active_grade

    @property
    def active_term(self) -> int:
        return self._active_term

    @property
    def active_key(self) -> str:
        return f"{self._active_grade}-{self._active_term}"

    # ================================================================
    # 课程信息
    # ================================================================

    def get_curriculum(self, grade: int = None, term: int = None) -> dict:
        """返回指定年级/学期的课程定义（units, label 等）"""
        g = grade if grade is not None else self._active_grade
        t = term if term is not None else self._active_term
        key = f"{g}-{t}"
        return self._data.get("curriculum", {}).get(key, {})

    def get_units(self, grade: int = None, term: int = None) -> dict:
        """返回单元映射 {序号: 名称}"""
        cur = self.get_curriculum(grade, term)
        units_list = cur.get("units", [])
        return {i + 1: name for i, name in enumerate(units_list)}

    # ================================================================
    # 基本属性
    # ================================================================

    @property
    def data(self):
        return self._data

    @property
    def grade_name(self) -> str:
        """年级名称，如'二年级'"""
        label = self.get_curriculum().get("label", "")
        for g in ["一", "二", "三", "四", "五", "六"]:
            if label.startswith(f"{g}年级"):
                return f"{g}年级"
        return f"{self._active_grade}年级"

    @property
    def grade_term(self) -> str:
        """学期，如'上册'/'下册'"""
        label = self.get_curriculum().get("label", "")
        if "上册" in label:
            return "上册"
        elif "下册" in label:
            return "下册"
        return "下册"

    @property
    def grade_label(self) -> str:
        """完整标签，如'二年级下册'"""
        return self.get_curriculum().get("label", f"{self._active_grade}年级")

    @property
    def textbook(self) -> str:
        return self._data.get("textbook", "北师大版")

    def get_sections(self):
        return self._data["exam"]["sections"]

    def get_db_path(self):
        db_rel = self._data["question_bank"]["db_path"]
        return str(self._project_root / db_rel)

    def get_output_dir(self):
        return str(self._project_root / "output")

    def get_seed_on_empty(self):
        return self._data["question_bank"].get("seed_on_empty", True)

    def get_sync_config(self):
        return self._data["question_bank"].get("sync", {})

    def get_rendering_config(self):
        return self._data["rendering"]

    def exam_title(self, week_label: str = "") -> str:
        template = self._data["exam"]["title_template"]
        title = template.format(
            textbook=self.textbook,
            grade_label=self.grade_label,
            term_label="",
            week=week_label,
        )
        return title
