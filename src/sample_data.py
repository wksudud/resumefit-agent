"""Load sample data for ResumeFit Agent demo."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_resume_text(path: str | None = None, language: str = "en") -> str:
    p = Path(path) if path else _localized_sample_path("sample_resume", language)
    return p.read_text(encoding="utf-8")


def load_jd_text(path: str | None = None, language: str = "en") -> str:
    p = Path(path) if path else _localized_sample_path("sample_jd", language)
    return p.read_text(encoding="utf-8")


def load_github_profile(path: str | None = None) -> dict:
    p = Path(path) if path else DATA_DIR / "github_profile.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_repo_docs(directory: str | None = None) -> dict[str, str]:
    d = Path(directory) if directory else DATA_DIR / "repositories"
    docs: dict[str, str] = {}
    if d.is_dir():
        for fpath in d.glob("*.md"):
            docs[fpath.stem] = fpath.read_text(encoding="utf-8")
    return docs


def load_sample_questionnaire() -> "RoleTendencyInput":
    """Load a default sample role tendency questionnaire for demo use."""
    from src.role_tendency import build_sample_questionnaire
    return build_sample_questionnaire()


def _localized_sample_path(stem: str, language: str) -> Path:
    if language == "zh":
        zh_path = DATA_DIR / f"{stem}.zh-CN.md"
        if zh_path.is_file():
            return zh_path
    return DATA_DIR / f"{stem}.md"
