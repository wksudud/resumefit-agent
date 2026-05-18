"""Verify evidence grounding of all recommendations."""

from src.schemas import (
    ResumeFitResult,
    VerifierReport,
    JDRequirementMatch,
    RewriteSuggestion,
    SkillGap,
)


def verify_result(result: ResumeFitResult) -> VerifierReport:
    violations: list[str] = []
    total = 0
    evidence_backed = 0
    assumption_flagged = 0

    # Check requirement matches
    for m in result.fit_report.requirement_matches:
        total += 1
        if m.status == "gap":
            if not m.assumption:
                violations.append(f"Gap '{m.requirement}' is not flagged as assumption-based")
            assumption_flagged += 1
        elif m.status == "partial":
            if m.assumption:
                assumption_flagged += 1
            elif m.evidence:
                evidence_backed += 1
            else:
                violations.append(f"Partial match '{m.requirement}' has no evidence and no assumption flag")
                assumption_flagged += 1
        elif m.status == "matched":
            if m.evidence:
                evidence_backed += 1
            else:
                violations.append(f"Matched requirement '{m.requirement}' lacks evidence")
                assumption_flagged += 1

    # Check rewrite suggestions
    for s in result.rewrite_suggestions:
        total += 1
        if s.honesty_note == "evidence-backed":
            evidence_backed += 1
        elif s.honesty_note == "assumption-based":
            assumption_flagged += 1
        else:
            violations.append(f"Rewrite suggestion for '{s.source_project}' has unclear honesty status")
            assumption_flagged += 1

    # Check skill gaps
    for g in result.skill_gaps:
        total += 1
        if g.proof_plan:
            evidence_backed += 1
        else:
            violations.append(f"Skill gap '{g.skill}' has no proof plan")
            assumption_flagged += 1

    # Check workflow trace completeness
    trace_steps = result.workflow_trace
    if len(trace_steps) < 6:
        violations.append(f"Workflow trace has only {len(trace_steps)} steps (expected 8+)")
    for step in trace_steps:
        if not step.verification:
            violations.append(f"Workflow step '{step.agent}' has no verification record")

    weak = total - evidence_backed - assumption_flagged
    passed = len(violations) == 0

    return VerifierReport(
        total_claims=total,
        evidence_backed=evidence_backed,
        assumption_flagged=assumption_flagged,
        weak_or_unverifiable=max(weak, 0),
        violations=violations,
        passed=passed,
    )
