from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


# ── Candidate ────────────────────────────────────────────────────────────────

@dataclass
class ResumeProfile:
    """Parsed resume information."""
    name: str
    target_role: str
    education: list[str]
    projects: list[ResumeProject]
    skills: list[str]
    achievements: list[str]
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "projects": [p.to_dict() for p in self.projects],
        }


@dataclass
class ResumeProject:
    name: str
    description: str
    technologies: list[str]
    highlights: list[str]
    role: str = "contributor"
    evidence_url: str = ""
    evidence_strength: str = "self_reported"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Job ──────────────────────────────────────────────────────────────────────

@dataclass
class JobProfile:
    """Parsed job description."""
    title: str
    company_hint: str
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    seniority_signal: str
    red_flags: list[str] = field(default_factory=list)
    hidden_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── GitHub Evidence ──────────────────────────────────────────────────────────

@dataclass
class ProjectEvidence:
    project_name: str
    source: str
    technologies: list[str]
    agent_llm_aiops_signals: list[str]
    measurable_proof: list[str]
    weak_evidence_warnings: list[str] = field(default_factory=list)
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Fit ──────────────────────────────────────────────────────────────────────

@dataclass
class JDRequirementMatch:
    requirement: str
    status: str  # matched | partial | gap
    evidence: list[str]
    assumption: bool = False
    warning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FitReport:
    overall_score: int
    score_label: str
    dimension_scores: dict[str, float]
    requirement_matches: list[JDRequirementMatch]
    matched_count: int
    partial_count: int
    gap_count: int
    risks: list[str]
    suggestions_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "requirement_matches": [m.to_dict() for m in self.requirement_matches],
        }


# ── Generated Artifacts ──────────────────────────────────────────────────────

@dataclass
class SkillGap:
    skill: str
    priority: str  # high | medium | low
    current_state: str
    target_state: str
    proof_plan: str
    suggested_resource: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RewriteSuggestion:
    source_project: str
    target_jd_requirement: str
    before_text: str
    after_text: str
    evidence: str
    honesty_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InterviewQuestion:
    question: str
    category: str  # skill_depth | project_detail | gap_probe | scenario
    target_weakness: str
    suggested_angle: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PortfolioCopy:
    short_card: str
    readme_tagline: str
    resume_bullets: list[str]
    project_story: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Workflow ─────────────────────────────────────────────────────────────────

@dataclass
class WorkflowStep:
    agent: str
    goal: str
    inputs: list[str]
    constraints: list[str]
    evidence: list[str]
    output: str
    assumptions: list[str] = field(default_factory=list)
    verification: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerifierReport:
    total_claims: int
    evidence_backed: int
    assumption_flagged: int
    weak_or_unverifiable: int
    violations: list[str]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Aggregate ────────────────────────────────────────────────────────────────

@dataclass
class ResumeFitResult:
    resume: ResumeProfile
    job: JobProfile
    evidence_items: list[ProjectEvidence]
    fit_report: FitReport
    rewrite_suggestions: list[RewriteSuggestion]
    skill_gaps: list[SkillGap]
    interview_questions: list[InterviewQuestion]
    portfolio_copy: PortfolioCopy
    workflow_trace: list[WorkflowStep]
    verifier_report: VerifierReport
    constraints: list[str]
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resume": self.resume.to_dict(),
            "job": self.job.to_dict(),
            "evidence_items": [e.to_dict() for e in self.evidence_items],
            "fit_report": self.fit_report.to_dict(),
            "rewrite_suggestions": [r.to_dict() for r in self.rewrite_suggestions],
            "skill_gaps": [g.to_dict() for g in self.skill_gaps],
            "interview_questions": [q.to_dict() for q in self.interview_questions],
            "portfolio_copy": self.portfolio_copy.to_dict(),
            "workflow_trace": [s.to_dict() for s in self.workflow_trace],
            "verifier_report": self.verifier_report.to_dict(),
            "constraints": self.constraints,
            "errors": self.errors,
        }


# ── Input ────────────────────────────────────────────────────────────────────

@dataclass
class ResumeFitInputs:
    resume_text: str
    jd_text: str
    github_profile_path: str
    repo_docs_dir: str
    output_report_path: str = "reports/fit_report.md"
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
