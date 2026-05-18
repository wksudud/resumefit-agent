"""Generate portfolio and README copy from fit analysis."""

from __future__ import annotations

from src.schemas import (
    FitReport,
    ResumeProfile,
    ProjectEvidence,
    PortfolioCopy,
)


def generate_portfolio_copy(
    fit_report: FitReport,
    resume: ResumeProfile | None = None,
    evidence_items: list[ProjectEvidence] | None = None,
) -> PortfolioCopy:
    name = resume.name if resume else "Candidate"
    role = resume.target_role if resume else "AI Engineer"
    score = fit_report.overall_score
    label = fit_report.score_label

    top_project = resume.projects[0].name if resume and resume.projects else "my AI project"

    short_card = (
        f"{name} | {role}\n\n"
        f"BUPT CS undergraduate building AI Agent applications and LLM-powered "
        f"workflows. Created {top_project}, a multi-agent system with evidence-traced "
        f"output and deterministic evaluation. Targeting {role} roles where "
        f"product-aware engineering meets practical AI.\n\n"
        f"Portfolio signal: {label} (score: {score}/100) against target JD."
    )

    readme_tagline = (
        f"{top_project}: An AI Agent workflow that demonstrates multi-agent "
        f"orchestration, evidence-grounded output, and disciplined software "
        f"engineering — built as a portfolio project for {role} roles."
    )

    resume_bullets = _generate_resume_bullets(resume, evidence_items, fit_report)

    project_story = (
        f"I built {top_project} to demonstrate practical AI Agent engineering skills "
        f"beyond simple API wrappers. The system uses a deterministic multi-agent "
        f"workflow with defined contracts between agents, step-level evidence "
        f"tracing, and a scoring rubric that makes quality measurable. "
        f"Every output is traceable to input evidence or flagged as an explicit "
        f"assumption. This project reflects my approach: product-aware engineering, "
        f"honest about limitations, and focused on building trustworthy AI systems."
    )

    return PortfolioCopy(
        short_card=short_card,
        readme_tagline=readme_tagline,
        resume_bullets=resume_bullets,
        project_story=project_story,
    )


def _generate_resume_bullets(
    resume: ResumeProfile | None,
    evidence_items: list[ProjectEvidence] | None,
    fit_report: FitReport,
) -> list[str]:
    bullets: list[str] = []

    if resume and resume.projects:
        for proj in resume.projects[:2]:
            tech_suffix = f" [{', '.join(proj.technologies[:3])}]" if proj.technologies else ""
            bullets.append(
                f"Built {proj.name}: a multi-agent AI workflow with structured "
                f"contracts, evidence tracing, and deterministic evaluation"
                f"{tech_suffix}"
            )

    bullets.append(
        f"Designed scoring rubric with 5 weighted dimensions (role alignment, "
        f"skill match, project evidence, GitHub proof, risk/honesty) for "
        f"transparent AI quality assessment"
    )

    bullets.append(
        "Implemented evidence verification pipeline: every recommendation "
        "traceable to source data or flagged as explicit assumption"
    )

    if evidence_items:
        strong = sum(1 for e in evidence_items if len(e.agent_llm_aiops_signals) >= 5)
        bullets.append(
            f"Demonstrated Agent/LLM/AIOps engineering across {strong}+ "
            f"projects with documented architecture and test coverage"
        )

    bullets.append(
        f"Package: Python, Streamlit, modular architecture with clean "
        f"interface contracts (dataclass-based schemas), smoke-testable "
        f"without network or API key dependencies"
    )

    return bullets
