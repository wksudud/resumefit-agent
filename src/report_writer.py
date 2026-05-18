"""Generate Markdown report from ResumeFitResult."""

from __future__ import annotations

from pathlib import Path
from src.schemas import ResumeFitResult


def write_markdown_report(result: ResumeFitResult, output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = _render_report(result)
    out.write_text(md, encoding="utf-8")
    return out


def render_report_text(result: ResumeFitResult) -> str:
    return _render_report(result)


def _render_report(result: ResumeFitResult) -> str:
    r = result.fit_report
    resume = result.resume
    job = result.job
    lines: list[str] = []

    lines.append("# ResumeFit Agent — Role Fit Report")
    lines.append("")
    lines.append(f"**Candidate:** {resume.name}")
    lines.append(f"**Target Role:** {resume.target_role}")
    lines.append(f"**Job Title:** {job.title}")
    lines.append(f"**Seniority:** {job.seniority_signal}")
    lines.append(f"**Generated:** {_now()}")
    lines.append("")

    # ── Overall Score ───────────────────────────────────────────────────
    lines.append("## 1. Role Match Score")
    lines.append("")
    lines.append(f"**Overall Score:** {r.overall_score}/100 — *{r.score_label}*")
    lines.append("")
    lines.append("### Dimension Scores")
    lines.append("")
    lines.append("| Dimension | Weight | Score |")
    lines.append("|---|---|---|")
    for dim, score in r.dimension_scores.items():
        label = dim.replace("_", " ").title()
        weight = _dim_weight(dim)
        lines.append(f"| {label} | {weight}% | {score} |")
    lines.append("")

    # ── Evidence Map ────────────────────────────────────────────────────
    lines.append("## 2. JD-to-Evidence Map")
    lines.append("")
    status_icon = {"matched": "[MATCH]", "partial": "[PARTIAL]", "gap": "[GAP]"}
    for m in r.requirement_matches:
        icon = status_icon.get(m.status, "[?]")
        lines.append(f"### {icon} {m.requirement}")
        lines.append(f"- **Status:** {m.status}")
        if m.evidence:
            for ev in m.evidence:
                lines.append(f"- **Evidence:** {ev}")
        if m.assumption:
            lines.append(f"- **Note:** Assumption-based assessment")
        if m.warning:
            lines.append(f"- **Warning:** {m.warning}")
        lines.append("")

    # ── Rewrite Suggestions ─────────────────────────────────────────────
    lines.append("## 3. Resume Project Rewrite Suggestions")
    lines.append("")
    for i, s in enumerate(result.rewrite_suggestions, 1):
        lines.append(f"### Suggestion {i}: {s.source_project}")
        lines.append(f"**Targets JD requirement:** {s.target_jd_requirement}")
        lines.append("")
        lines.append(f"**Before:**")
        lines.append(f"> {s.before_text}")
        lines.append("")
        lines.append(f"**After:**")
        lines.append(f"> {s.after_text}")
        lines.append("")
        lines.append(f"**Evidence:** {s.evidence}")
        lines.append(f"**Honesty check:** {s.honesty_note}")
        lines.append("")

    # ── Skill Gaps ──────────────────────────────────────────────────────
    lines.append("## 4. Skill Gaps and Proof Plan")
    lines.append("")
    if result.skill_gaps:
        lines.append("| Skill | Priority | Current State | Target | Proof Plan |")
        lines.append("|---|---|---|---|---|")
        for g in result.skill_gaps:
            lines.append(f"| {g.skill} | {g.priority} | {g.current_state} | {g.target_state} | {g.proof_plan} |")
    else:
        lines.append("*No significant skill gaps identified.*")
    lines.append("")

    # ── Interview Questions ─────────────────────────────────────────────
    lines.append("## 5. Interview Follow-Up Questions")
    lines.append("")
    for i, q in enumerate(result.interview_questions, 1):
        lines.append(f"### Q{i}: {q.question}")
        lines.append(f"- **Category:** {q.category}")
        lines.append(f"- **Targets:** {q.target_weakness}")
        if q.suggested_angle:
            lines.append(f"- **Suggested angle:** {q.suggested_angle}")
        lines.append("")

    # ── Portfolio Copy ──────────────────────────────────────────────────
    lines.append("## 6. Portfolio Display Copy")
    lines.append("")
    pc = result.portfolio_copy
    lines.append("### Short Card")
    lines.append("```")
    lines.append(pc.short_card)
    lines.append("```")
    lines.append("")
    lines.append("### README Tagline")
    lines.append(f"> {pc.readme_tagline}")
    lines.append("")
    lines.append("### Resume Bullets")
    for b in pc.resume_bullets:
        lines.append(f"- {b}")
    lines.append("")
    lines.append("### Project Story")
    lines.append(pc.project_story)
    lines.append("")

    # ── Workflow Trace ──────────────────────────────────────────────────
    lines.append("## 7. Workflow Trace")
    lines.append("")
    for step in result.workflow_trace:
        lines.append(f"### {step.agent}")
        lines.append(f"- **Goal:** {step.goal}")
        lines.append(f"- **Inputs:** {', '.join(step.inputs) if step.inputs else 'N/A'}")
        lines.append(f"- **Constraints:** {', '.join(step.constraints) if step.constraints else 'N/A'}")
        lines.append(f"- **Evidence:** {', '.join(step.evidence) if step.evidence else 'N/A'}")
        lines.append(f"- **Output:** {step.output}")
        if step.assumptions:
            lines.append(f"- **Assumptions:** {', '.join(step.assumptions)}")
        if step.verification:
            lines.append(f"- **Verification:** {step.verification}")
        lines.append("")

    # ── Verifier Report ─────────────────────────────────────────────────
    lines.append("## 8. Evidence Verification")
    lines.append("")
    vr = result.verifier_report
    lines.append(f"- **Total claims:** {vr.total_claims}")
    lines.append(f"- **Evidence-backed:** {vr.evidence_backed}")
    lines.append(f"- **Assumption-flagged:** {vr.assumption_flagged}")
    lines.append(f"- **Weak/unverifiable:** {vr.weak_or_unverifiable}")
    lines.append(f"- **Passed:** {'Yes' if vr.passed else 'No'}")
    if vr.violations:
        lines.append("")
        lines.append("### Violations")
        for v in vr.violations:
            lines.append(f"- {v}")
    lines.append("")

    # ── Risks ───────────────────────────────────────────────────────────
    lines.append("## 9. Risks and Constraints")
    lines.append("")
    if result.fit_report.risks:
        for risk in result.fit_report.risks:
            lines.append(f"- {risk}")
    if result.constraints:
        lines.append("")
        lines.append("### Declared Constraints")
        for c in result.constraints:
            lines.append(f"- {c}")
    lines.append("")

    # ── Footer ──────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by ResumeFit Agent — deterministic core workflow prototype.*")
    lines.append("*Sample data used. All recommendations are evidence-grounded or explicitly assumption-flagged.*")
    lines.append("*No real resume data, credentials, or paid APIs were used in this generation.*")
    lines.append("")

    return "\n".join(lines)


def _dim_weight(dim: str) -> int:
    weights = {
        "role_alignment": 25,
        "core_skill_match": 25,
        "project_evidence": 25,
        "github_proof": 15,
        "risk_honesty": 10,
    }
    return weights.get(dim, 0)


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
