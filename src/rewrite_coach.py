"""Generate resume project rewrite suggestions."""

from __future__ import annotations

from src.schemas import (
    ResumeProfile,
    FitReport,
    RewriteSuggestion,
    JDRequirementMatch,
)


def suggest_rewrites(
    fit_report: FitReport,
    resume: ResumeProfile,
) -> list[RewriteSuggestion]:
    suggestions: list[RewriteSuggestion] = []

    partial_matches = [m for m in fit_report.requirement_matches if m.status == "partial"]
    gap_matches = [m for m in fit_report.requirement_matches if m.status == "gap"]

    for project in resume.projects:
        for req_match in partial_matches[:3] + gap_matches[:2]:
            req_text = req_match.requirement
            before = _pick_before_text(project, req_text)
            after = _generate_after_text(project, req_text, req_match)
            evidence = _find_evidence(project, req_match)
            honesty = "evidence-backed" if not req_match.assumption else "assumption-based"

            suggestions.append(RewriteSuggestion(
                source_project=project.name,
                target_jd_requirement=req_text,
                before_text=before,
                after_text=after,
                evidence=evidence,
                honesty_note=honesty,
            ))

    return suggestions


def _pick_before_text(project, req_text: str) -> str:
    if project.highlights:
        return project.highlights[0]
    return project.description[:120] if project.description else project.name


def _generate_after_text(project, req_text: str, req_match: JDRequirementMatch) -> str:
    name = project.name
    tech = ", ".join(project.technologies[:3]) if project.technologies else "Python"
    req_lower = req_text.lower()

    templates = []

    if "agent" in req_lower or "workflow" in req_lower or "orchestrat" in req_lower:
        templates.append(
            f"Designed and implemented a multi-agent workflow in {name} "
            f"with defined input/output contracts between agents, "
            f"step-level evidence tracing, and deterministic fallback paths. "
            f"Built with {tech}."
        )
    if "llm" in req_lower or "prompt" in req_lower:
        templates.append(
            f"Integrated LLM capabilities into {name} using structured prompt "
            f"templates with output validation. Applied prompt engineering "
            f"patterns for consistent, traceable generation."
        )
    if "rag" in req_lower or "retrieval" in req_lower:
        templates.append(
            f"Implemented a retrieval-augmented generation pipeline in {name} "
            f"with local document chunking, embedding-based search, and "
            f"citation-linked answer generation."
        )
    if "streamlit" in req_lower or "dashboard" in req_lower or "ui" in req_lower:
        templates.append(
            f"Built an interactive {name} dashboard using Streamlit with "
            f"structured tabs for data input, analysis results, evidence "
            f"inspection, and report export."
        )
    if "document" in req_lower or "readme" in req_lower:
        templates.append(
            f"Authored comprehensive documentation for {name} including "
            f"architecture diagrams, setup guide, API contracts, and "
            f"evidence-trace examples in the project README."
        )
    if "eval" in req_lower or "metric" in req_lower or "quality" in req_lower:
        templates.append(
            f"Developed an evidence verification framework for {name} that "
            f"checks every output claim against source data, flags "
            f"assumptions, and tracks verification status per workflow step."
        )
    if "docker" in req_lower or "container" in req_lower:
        templates.append(
            f"Containerized {name} with Docker for reproducible deployment, "
            f"including multi-stage builds and environment isolation for "
            f"dependency management."
        )
    if "git" in req_lower or "version control" in req_lower:
        templates.append(
            f"Managed {name} development with Git-based version control, "
            f"structured commit history, and branch-per-feature workflow."
        )

    if templates:
        return templates[0]

    # Generic template
    return (
        f"Applied software engineering best practices to {name}: "
        f"structured project layout, clean module interfaces (via dataclasses), "
        f"deterministic testing without external API dependencies, and "
        f"evidence-traced output generation. Built with {tech}."
    )


def _find_evidence(project, req_match: JDRequirementMatch) -> str:
    if req_match.evidence:
        return "; ".join(req_match.evidence)
    return f"Based on project {project.name} description and technology stack"
