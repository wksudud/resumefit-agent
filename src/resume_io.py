"""Resume upload parsing and rewritten resume export helpers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from docx import Document

from src.schemas import RewriteSuggestion


SUPPORTED_RESUME_TYPES = ("md", "markdown", "docx", "doc")


def read_uploaded_resume(uploaded_file) -> tuple[str, str | None]:
    """Extract text from a Streamlit uploaded resume file.

    Legacy .doc files are intentionally not parsed because Streamlit Cloud does
    not provide a reliable pure-Python parser for the binary Word format.
    """
    if uploaded_file is None:
        return "", None

    file_name = getattr(uploaded_file, "name", "")
    suffix = Path(file_name).suffix.lower().lstrip(".")
    raw_bytes = _read_all(uploaded_file)

    if suffix in {"md", "markdown"}:
        return _decode_text(raw_bytes), None

    if suffix == "docx":
        document = Document(BytesIO(raw_bytes))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs), None

    if suffix == "doc":
        return "", "legacy_doc"

    return "", "unsupported"


def build_rewritten_resume_markdown(
    original_text: str,
    suggestions: list[RewriteSuggestion],
    language: str = "en",
) -> str:
    """Build a conservative rewritten-resume artifact from original text and suggestions."""
    labels = {
        "en": {
            "title": "Rewritten Resume Draft",
            "source": "Original Resume",
            "suggestions": "Rewrite Suggestions",
            "note": "Review each suggestion before using it in an application.",
            "before": "Before",
            "after": "After",
            "evidence": "Evidence",
        },
        "zh": {
            "title": "改写后简历草稿",
            "source": "原始简历",
            "suggestions": "改写建议",
            "note": "投递前请逐条核对事实与表述。",
            "before": "改写前",
            "after": "改写后",
            "evidence": "证据",
        },
    }.get(language, {})

    parts = [
        f"# {labels.get('title', 'Rewritten Resume Draft')}",
        f"> {labels.get('note', 'Review each suggestion before using it in an application.')}",
        "",
        f"## {labels.get('source', 'Original Resume')}",
        original_text.strip() or "_No resume text captured._",
        "",
        f"## {labels.get('suggestions', 'Rewrite Suggestions')}",
    ]

    if not suggestions:
        parts.append("_No rewrite suggestions generated._")
    else:
        for index, suggestion in enumerate(suggestions, 1):
            parts.extend([
                "",
                f"### {index}. {suggestion.source_project}",
                f"**{labels.get('before', 'Before')}:** {suggestion.before_text}",
                "",
                f"**{labels.get('after', 'After')}:** {suggestion.after_text}",
                "",
                f"**{labels.get('evidence', 'Evidence')}:** {suggestion.evidence}",
            ])

    return "\n".join(parts).strip() + "\n"


def build_rewritten_resume_docx(markdown_text: str) -> bytes:
    """Convert the generated Markdown draft into a simple Word document."""
    document = Document()

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            document.add_heading(stripped[2:], level=1)
        elif stripped.startswith("## "):
            document.add_heading(stripped[3:], level=2)
        elif stripped.startswith("### "):
            document.add_heading(stripped[4:], level=3)
        elif stripped.startswith("> "):
            document.add_paragraph(stripped[2:], style="Intense Quote")
        elif stripped.startswith("- "):
            document.add_paragraph(stripped[2:], style="List Bullet")
        else:
            document.add_paragraph(_strip_basic_markdown(stripped))

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _read_all(uploaded_file) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()
    if isinstance(uploaded_file, (bytes, bytearray)):
        return bytes(uploaded_file)
    if isinstance(uploaded_file, BinaryIO):
        return uploaded_file.read()
    return uploaded_file.read()


def _decode_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def _strip_basic_markdown(text: str) -> str:
    return (
        text.replace("**", "")
        .replace("__", "")
        .replace("`", "")
    )
