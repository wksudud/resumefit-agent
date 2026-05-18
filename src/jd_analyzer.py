"""Parse job description markdown into a JobProfile."""

from __future__ import annotations

import re

from src.schemas import JobProfile


def analyze_jd(text: str) -> JobProfile:
    sections = _split_sections(text)

    position_section = sections.get("Position", "")
    title = _extract_first_line(position_section) or "Software Engineer"

    company = _extract_first_line(sections.get("Company Context", "")) or "Unknown"

    required = _extract_bullets(sections.get("Required Skills", ""))
    preferred = _extract_bullets(sections.get("Preferred Skills", ""))
    responsibilities = _extract_bullets(sections.get("Responsibilities", ""))

    seniority_section = sections.get("Seniority", "")
    seniority = seniority_section.strip() if seniority_section else "entry"

    red_flags_raw = _extract_bullets(sections.get("Red Flags for This Role", ""))
    if not red_flags_raw:
        red_flags_raw = _extract_bullets(sections.get("Red Flags", ""))

    hidden_signals = _derive_hidden_signals(required, preferred, responsibilities, red_flags_raw)

    return JobProfile(
        title=title,
        company_hint=company,
        required_skills=required,
        preferred_skills=preferred,
        responsibilities=responsibilities,
        seniority_signal=seniority,
        red_flags=red_flags_raw,
        hidden_signals=hidden_signals,
    )


def _split_sections(text: str) -> dict[str, str]:
    parts = re.split(r"\n## ", text)
    result: dict[str, str] = {}
    for part in parts:
        part = part.strip()
        m = re.match(r"(.+?)\n", part)
        if m:
            title = m.group(1).strip()
            body = part[m.end():].strip()
            result[title] = body
    return result


def _extract_first_line(section: str) -> str:
    for line in section.split("\n"):
        s = _clean_markdown_value(line)
        if s:
            return s
    return ""


def _extract_bullets(section: str) -> list[str]:
    items: list[str] = []
    for line in section.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _clean_markdown_value(value: str) -> str:
    cleaned = value.strip()
    cleaned = cleaned.lstrip("- ").strip()
    cleaned = cleaned.lstrip(":：").strip()
    cleaned = re.sub(r"^\*+|\*+$", "", cleaned).strip()
    cleaned = cleaned.replace("**", "").strip()
    return cleaned


def _derive_hidden_signals(
    required: list[str],
    preferred: list[str],
    responsibilities: list[str],
    red_flags: list[str],
) -> list[str]:
    signals: list[str] = []
    all_text = " ".join(required + preferred + responsibilities + red_flags).lower()

    if any(kw in all_text for kw in ["agent", "workflow", "orchestrat"]):
        signals.append("Values agent architecture design over simple API wrapping")
    if any(kw in all_text for kw in ["evidence", "evaluation", "eval", "metric"]):
        signals.append("Expects measurable quality assessment, not just generation")
    if any(kw in all_text for kw in ["portfolio", "github", "open source", "project"]):
        signals.append("Uses GitHub/portfolio as primary signal for capability")
    if any(kw in all_text for kw in ["product", "user need", "business"]):
        signals.append("Looking for product-aware engineers, not pure researchers")
    if any(kw in all_text for kw in ["domain", "telecom", "vertical"]):
        signals.append("Values domain-specific AI application over generic solutions")
    if any(kw in all_text for kw in ["document", "readme", "communicat"]):
        signals.append("Technical communication skill is a real evaluation criterion")
    if any(kw in all_text for kw in ["learning ability", "junior", "intern", "grow"]):
        signals.append("Values growth potential and learning speed over years of experience")
    if not signals:
        signals.append("Standard engineering evaluation signals expected")

    return signals
