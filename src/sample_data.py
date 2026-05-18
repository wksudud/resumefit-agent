"""Load sample data for ResumeFit Agent demo."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_resume_text(path: str | None = None) -> str:
    p = Path(path) if path else DATA_DIR / "sample_resume.md"
    return p.read_text(encoding="utf-8")


def load_jd_text(path: str | None = None) -> str:
    p = Path(path) if path else DATA_DIR / "sample_jd.md"
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
