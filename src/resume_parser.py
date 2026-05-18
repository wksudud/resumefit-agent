"""Parse resume markdown text into a ResumeProfile."""

from __future__ import annotations

import re

from src.schemas import ResumeProfile, ResumeProject


def parse_resume(text: str) -> ResumeProfile:
    sections = _split_sections(text)

    profile = ResumeProfile(
        name=_extract_field(sections.get("Contact", ""), "Name", "Unknown"),
        target_role=_extract_field(sections.get("Contact", ""), "Target Role", "AI Engineer"),
        education=_extract_bullets(sections.get("Education", "")),
        projects=_parse_projects(sections.get("Projects", "")),
        skills=_extract_bullets(sections.get("Skills", "")),
        achievements=_extract_bullets(sections.get("Achievements", "")),
        constraints=_extract_bullets(sections.get("Constraints", "")),
    )
    return profile


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


def _extract_field(section: str, label: str, default: str = "") -> str:
    m = re.search(rf"\*\*{re.escape(label)}\*\*\s*(.+)", section)
    return _clean_markdown_value(m.group(1)) if m else default


def _extract_bullets(section: str) -> list[str]:
    items: list[str] = []
    for line in section.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _parse_projects(section: str) -> list[ResumeProject]:
    projects: list[ResumeProject] = []
    blocks = re.split(r"\n### ", section)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        name = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:])

        desc_lines: list[str] = []
        tech_list: list[str] = []
        highlights: list[str] = []

        for line in body.split("\n"):
            s = line.strip()
            item = s[2:].strip() if s.startswith("- ") else s
            if item.lower().startswith("technologies:") or item.lower().startswith("tech:"):
                tech_str = item.split(":", 1)[1].strip() if ":" in item else ""
                tech_str = tech_str.rstrip(".")
                tech_list = [t.strip() for t in tech_str.replace("、", ",").split(",") if t.strip()]
            elif s.startswith("- "):
                highlights.append(s[2:].strip())
            elif s:
                desc_lines.append(s)

        description = " ".join(desc_lines)
        if not description:
            description = _extract_field(body, "Description", name)

        if name:
            projects.append(ResumeProject(
                name=name,
                description=description,
                technologies=tech_list,
                highlights=highlights,
                role="contributor",
                evidence_url="",
                evidence_strength="self_reported",
            ))

    return projects


def _clean_markdown_value(value: str) -> str:
    cleaned = value.strip()
    cleaned = cleaned.lstrip(":：").strip()
    cleaned = re.sub(r"^\*+|\*+$", "", cleaned).strip()
    return cleaned
