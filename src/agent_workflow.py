"""Orchestrate the full ResumeFit Agent workflow."""

from __future__ import annotations

import json
from pathlib import Path

from src.schemas import (
    ResumeFitInputs,
    ResumeFitResult,
    WorkflowStep,
    VerifierReport,
)
from src.resume_parser import parse_resume
from src.jd_analyzer import analyze_jd
from src.github_evidence import extract_github_evidence
from src.fit_scoring import score_fit
from src.rewrite_coach import suggest_rewrites
from src.interview_prep import generate_interview_questions
from src.portfolio_copy import generate_portfolio_copy
from src.verifier import verify_result


def run_resume_fit_workflow(inputs: ResumeFitInputs) -> ResumeFitResult:
    constraints = inputs.constraints or []
    trace: list[WorkflowStep] = []
    errors: list[str] = []

    # Step 1: Parse Resume
    try:
        resume = parse_resume(inputs.resume_text)
        trace.append(WorkflowStep(
            agent="Resume Parser",
            goal="Extract candidate facts, projects, skills, constraints from resume text",
            inputs=["resume_text"],
            constraints=["Markdown format expected", "Sample data only"],
            evidence=["Section-based parsing with regex"],
            output=f"Parsed {len(resume.projects)} projects, {len(resume.skills)} skills",
            assumptions=[],
            verification="ResumeProfile created with non-empty fields",
        ))
    except Exception as e:
        errors.append(f"Resume parsing failed: {e}")
        return _error_result(inputs, trace, errors, "Resume parsing failure")

    # Step 2: Analyze JD
    try:
        job = analyze_jd(inputs.jd_text)
        trace.append(WorkflowStep(
            agent="JD Analyzer",
            goal="Extract requirements, skills, responsibilities, hidden signals from JD",
            inputs=["jd_text"],
            constraints=["Markdown format expected", "Deterministic extraction only"],
            evidence=["Section parsing, keyword-based signal derivation"],
            output=f"Extracted {len(job.required_skills)} required, {len(job.preferred_skills)} preferred skills",
            assumptions=[],
            verification="JobProfile created with required/preferred skills populated",
        ))
    except Exception as e:
        errors.append(f"JD analysis failed: {e}")
        return _error_result(inputs, trace, errors, "JD analysis failure")

    # Step 3: GitHub Evidence
    try:
        github_profile = _load_json(inputs.github_profile_path)
        repo_docs = _load_repo_docs(inputs.repo_docs_dir)
        evidence_items = extract_github_evidence(github_profile, repo_docs)
        trace.append(WorkflowStep(
            agent="GitHub Evidence Agent",
            goal="Map repository metadata and docs to project evidence signals",
            inputs=["github_profile.json", "repositories/*.md"],
            constraints=["Local/metadata only", "No GitHub API calls", "Read-only"],
            evidence=["Keyword scanning for Agent/LLM/AIOps signals", "Metadata quality checks"],
            output=f"Extracted evidence for {len(evidence_items)} repositories",
            assumptions=["Repo docs are user-provided summaries", "GitHub metrics are sample data"],
            verification=f"{len(evidence_items)} ProjectEvidence items created",
        ))
    except Exception as e:
        errors.append(f"GitHub evidence extraction failed: {e}")
        return _error_result(inputs, trace, errors, "GitHub evidence failure")

    # Step 4: Fit Scoring
    try:
        fit_report = score_fit(resume, job, evidence_items)
        trace.append(WorkflowStep(
            agent="Fit Scoring Agent",
            goal="Apply weighted rubric: role alignment, skill match, project evidence, GitHub proof, risk",
            inputs=["ResumeProfile", "JobProfile", "list[ProjectEvidence]"],
            constraints=["Deterministic keyword matching", "No fabricated metrics"],
            evidence=[
                f"Rubric weights: role=25%, skill=25%, project=25%, GitHub=15%, risk=10%",
                f"Matched={fit_report.matched_count}, partial={fit_report.partial_count}, gaps={fit_report.gap_count}",
            ],
            output=f"Score: {fit_report.overall_score}/100 — {fit_report.score_label}",
            assumptions=["Keyword matching is approximate", "Absence of signal = gap, not negative"],
            verification=f"FitReport generated with {len(fit_report.requirement_matches)} requirement matches",
        ))
    except Exception as e:
        errors.append(f"Fit scoring failed: {e}")
        return _error_result(inputs, trace, errors, "Fit scoring failure")

    # Step 5: Rewrite Suggestions
    try:
        rewrites = suggest_rewrites(fit_report, resume)
        trace.append(WorkflowStep(
            agent="Rewrite Coach Agent",
            goal="Generate before/after project bullet rewrites targeting JD requirements",
            inputs=["FitReport", "ResumeProfile"],
            constraints=["No fabricated achievements", "Conservative language for unverified claims"],
            evidence=[f"Based on {fit_report.partial_count} partial + {fit_report.gap_count} gap requirements"],
            output=f"Generated {len(rewrites)} rewrite suggestions with evidence annotation",
            assumptions=["Rewrites preserve factual accuracy", "After text is a conservative improvement"],
            verification=f"{len(rewrites)} RewriteSuggestion items with honesty checks",
        ))
    except Exception as e:
        errors.append(f"Rewrite generation failed: {e}")
        rewrites = []

    # Step 6: Skill Gaps
    skill_gaps = _generate_skill_gaps(fit_report, resume, evidence_items)
    trace.append(WorkflowStep(
        agent="Skill Gap Agent",
        goal="Identify skill gaps, prioritize, and propose proof-building plans",
        inputs=["FitReport", "ResumeProfile", "list[ProjectEvidence]"],
        constraints=["Gap priority based on JD requirement importance"],
        evidence=[f"Derived from {fit_report.gap_count} gaps in requirement matching"],
        output=f"Identified {len(skill_gaps)} skill gaps with proof plans",
        assumptions=["Proof plans are suggestions requiring candidate follow-through"],
        verification=f"{len(skill_gaps)} SkillGap items with priority and proof plans",
    ))

    # Step 7: Interview Questions
    try:
        interview_qs = generate_interview_questions(fit_report, resume, evidence_items)
        trace.append(WorkflowStep(
            agent="Interview Prep Agent",
            goal="Generate likely follow-up questions targeting gaps and weak signals",
            inputs=["FitReport", "ResumeProfile", "list[ProjectEvidence]"],
            constraints=["Questions should probe real weaknesses", "Provide answer angles"],
            evidence=[f"Based on {fit_report.gap_count} gaps and {fit_report.partial_count} partial matches"],
            output=f"Generated {len(interview_qs)} interview questions with answer angles",
            assumptions=["Questions are predictive, not from real interview data"],
            verification=f"{len(interview_qs)} InterviewQuestion items across categories",
        ))
    except Exception as e:
        errors.append(f"Interview question generation failed: {e}")
        interview_qs = []

    # Step 8: Portfolio Copy
    try:
        portfolio = generate_portfolio_copy(fit_report, resume, evidence_items)
        trace.append(WorkflowStep(
            agent="Portfolio Copy Agent",
            goal="Generate homepage/README-ready copy, resume bullets, and project story",
            inputs=["FitReport", "ResumeProfile", "list[ProjectEvidence]"],
            constraints=["Truthful representation", "No fabricated metrics"],
            evidence=["Based on project evidence and fit analysis"],
            output=f"Portfolio copy with {len(portfolio.resume_bullets)} resume bullets",
            assumptions=["Copy should be reviewed by candidate before real use"],
            verification="PortfolioCopy generated with all sections populated",
        ))
    except Exception as e:
        errors.append(f"Portfolio copy generation failed: {e}")
        portfolio = None

    # Step 9: Verifier
    result = ResumeFitResult(
        resume=resume,
        job=job,
        evidence_items=evidence_items,
        fit_report=fit_report,
        rewrite_suggestions=rewrites,
        skill_gaps=skill_gaps,
        interview_questions=interview_qs,
        portfolio_copy=portfolio,
        workflow_trace=trace,
        verifier_report=VerifierReport(0, 0, 0, 0, [], True),
        constraints=constraints,
    )
    verifier_report = verify_result(result)
    result.verifier_report = verifier_report

    trace.append(WorkflowStep(
        agent="Verifier",
        goal="Check that every recommendation has evidence or is flagged as assumption",
        inputs=["ResumeFitResult"],
        constraints=["No fabricated evidence permitted"],
        evidence=[f"Checked {verifier_report.total_claims} claims"],
        output=f"Passed: {verifier_report.passed}, violations: {len(verifier_report.violations)}",
        assumptions=[],
        verification=f"VerifierReport: {verifier_report.evidence_backed} evidence-backed, "
                     f"{verifier_report.assumption_flagged} assumption-flagged",
    ))

    if errors:
        result.errors = errors

    return result


def _generate_skill_gaps(fit_report, resume, evidence_items):
    """Deterministic skill gap identification."""
    from src.schemas import SkillGap

    gaps: list[SkillGap] = []
    gap_matches = [m for m in fit_report.requirement_matches if m.status == "gap"]
    partial_matches = [m for m in fit_report.requirement_matches if m.status == "partial"]

    gap_templates = {
        "evaluation": SkillGap(
            skill="LLM Output Evaluation",
            priority="high",
            current_state="No formal evaluation framework demonstrated",
            target_state="Build an eval harness measuring accuracy, faithfulness, relevance",
            proof_plan="Create a benchmark script for project outputs with pass/fail criteria and metrics",
            suggested_resource="Open source: DeepEval, RAGAS, or custom rubric-based eval",
        ),
        "docker": SkillGap(
            skill="Docker / Containerization",
            priority="medium",
            current_state="Docker listed as learning, not demonstrated in projects",
            target_state="Containerize one project with Dockerfile and docker-compose",
            proof_plan="Add Dockerfile and docker-compose.yml to TelecomOps Agent or ResumeFit Agent repo",
            suggested_resource="Docker official getting-started guide, multi-stage build patterns",
        ),
        "testing": SkillGap(
            skill="Automated Testing",
            priority="medium",
            current_state="Limited test infrastructure in projects",
            target_state="Add pytest coverage for core workflow and scoring logic",
            proof_plan="Write unit tests for fit_scoring.py and integration test for agent_workflow.py",
            suggested_resource="pytest documentation, test fixtures and parametrize patterns",
        ),
        "ci_cd": SkillGap(
            skill="CI/CD Pipelines",
            priority="medium",
            current_state="No CI/CD demonstrated",
            target_state="Add GitHub Actions workflow for lint, test, smoke",
            proof_plan="Create .github/workflows/ci.yml with pytest and smoke test steps",
            suggested_resource="GitHub Actions quickstart, Python CI template",
        ),
        "api": SkillGap(
            skill="API Design (FastAPI/REST)",
            priority="low",
            current_state="No API design experience demonstrated",
            target_state="Add FastAPI wrapper around core workflow for headless access",
            proof_plan="Create api.py with /analyze endpoint wrapping run_resume_fit_workflow",
            suggested_resource="FastAPI tutorial, pydantic request/response models",
        ),
    }

    gap_texts = " ".join(g.requirement.lower() for g in gap_matches)
    partial_texts = " ".join(p.requirement.lower() for p in partial_matches)
    all_texts = gap_texts + " " + partial_texts
    added = set()

    for key, template in gap_templates.items():
        keywords = {
            "evaluation": ["eval", "metric", "quality"],
            "docker": ["docker", "container"],
            "testing": ["test", "pytest"],
            "ci_cd": ["ci/cd", "ci", "github action"],
            "api": ["api", "fastapi", "rest"],
        }
        kws = keywords.get(key, [])
        if any(kw in all_texts for kw in kws) and key not in added:
            gaps.append(template)
            added.add(key)

    # Always include evaluation gap for candidates with limited GitHub proof
    if "evaluation" not in added:
        gaps.append(gap_templates["evaluation"])
        added.add("evaluation")
    if "testing" not in added:
        gaps.append(gap_templates["testing"])
        added.add("testing")

    return gaps


def _load_json(path: str) -> dict:
    p = Path(path)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"GitHub profile not found: {path}")


def _load_repo_docs(directory: str) -> dict[str, str]:
    d = Path(directory)
    docs: dict[str, str] = {}
    if d.is_dir():
        for fpath in d.glob("*.md"):
            docs[fpath.stem] = fpath.read_text(encoding="utf-8")
    return docs


def _error_result(inputs, trace, errors, reason) -> ResumeFitResult:
    from src.schemas import (
        ResumeProfile, JobProfile, FitReport, PortfolioCopy, VerifierReport,
    )
    return ResumeFitResult(
        resume=ResumeProfile("Error", "", [], [], [], [], []),
        job=JobProfile("Error", "", [], [], [], "", [], []),
        evidence_items=[],
        fit_report=FitReport(0, "error", {}, [], 0, 0, 0, [], ""),
        rewrite_suggestions=[],
        skill_gaps=[],
        interview_questions=[],
        portfolio_copy=PortfolioCopy("Error", "Error", [], "Error"),
        workflow_trace=trace,
        verifier_report=VerifierReport(0, 0, 0, 0, [reason], False),
        constraints=inputs.constraints or [],
        errors=errors,
    )


def run_and_write_report(
    resume_path: str | None = None,
    jd_path: str | None = None,
    github_path: str | None = None,
    repo_docs_dir: str | None = None,
    output_path: str = "reports/fit_report.md",
) -> ResumeFitResult:
    """Convenience: run full workflow with default sample data and write Markdown report."""
    from src.sample_data import load_resume_text, load_jd_text
    from src.report_writer import write_markdown_report

    resume_text = load_resume_text(resume_path)
    jd_text = load_jd_text(jd_path)
    gh_path = github_path or "data/github_profile.json"
    docs_dir = repo_docs_dir or "data/repositories"

    inputs = ResumeFitInputs(
        resume_text=resume_text,
        jd_text=jd_text,
        github_profile_path=gh_path,
        repo_docs_dir=docs_dir,
        output_report_path=output_path,
        constraints=[
            "no_network_calls",
            "no_api_keys",
            "sample_synthetic_data_only",
            "deterministic_rules_only_no_llm",
            "telecomops_agent_is_read_only_reference",
        ],
    )
    result = run_resume_fit_workflow(inputs)
    write_markdown_report(result, Path(output_path))
    return result
