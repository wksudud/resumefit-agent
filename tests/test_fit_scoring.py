"""Unit tests for fit_scoring module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schemas import (
    ResumeProfile, ResumeProject, JobProfile, ProjectEvidence,
    JDRequirementMatch, FitReport,
)
from src.fit_scoring import (
    score_fit, _score_role_alignment, _score_skill_match,
    _score_project_evidence, _score_github_proof, _score_risk_honesty,
    _label, _build_requirement_list, _match_requirements,
)


def make_resume():
    return ResumeProfile(
        name="Test User",
        target_role="AI Agent Engineer",
        education=["B.Eng. CS"],
        projects=[
            ResumeProject("Test Agent", "An agent project", ["Python"], ["built agent"], "contributor"),
        ],
        skills=["Python", "Git", "LLM APIs", "Prompt Engineering", "Streamlit", "Docker"],
        achievements=["Built agent project"],
        constraints=["No internship"],
    )


def make_job():
    return JobProfile(
        title="AI Agent Application Engineer",
        company_hint="Tech Corp",
        required_skills=["Python", "LLM APIs", "Agent architecture"],
        preferred_skills=["Streamlit", "RAG", "Docker"],
        responsibilities=["Design agent workflows", "Build LLM apps"],
        seniority_signal="Junior / Intern",
        red_flags=["Only model training without application"],
        hidden_signals=["Values agent architecture"],
    )


def make_evidence():
    return [
        ProjectEvidence(
            project_name="test-agent",
            source="An agent project",
            technologies=["Python", "Streamlit"],
            agent_llm_aiops_signals=["agent", "workflow", "orchestrat", "llm", "prompt"],
            measurable_proof=["18 commits", "Has README", "Has tests"],
            weak_evidence_warnings=["Not public"],
            read_only=True,
        ),
    ]


class TestLabel:
    def test_strong(self):
        assert "strong match" in _label(85)

    def test_plausible(self):
        assert "plausible" in _label(65)

    def test_partial(self):
        assert "partial match" in _label(50)

    def test_not_recommended(self):
        assert "not recommended" in _label(30)


class TestScoreFit:
    def test_returns_fit_report(self):
        result = score_fit(make_resume(), make_job(), make_evidence())
        assert isinstance(result, FitReport)
        assert 0 <= result.overall_score <= 100
        assert len(result.dimension_scores) == 5
        assert len(result.requirement_matches) > 0

    def test_score_in_plausible_range(self):
        result = score_fit(make_resume(), make_job(), make_evidence())
        assert 50 <= result.overall_score <= 85

    def test_empty_evidence_lower_score(self):
        result = score_fit(make_resume(), make_job(), [])
        assert result.overall_score < 80


class TestRequirementMatching:
    def test_all_statuses_present(self):
        matches = _match_requirements(
            _build_requirement_list(make_job()),
            make_resume(),
            make_evidence(),
        )
        statuses = {m.status for m in matches}
        assert "matched" in statuses

    def test_every_match_has_evidence_or_assumption(self):
        matches = _match_requirements(
            _build_requirement_list(make_job()),
            make_resume(),
            make_evidence(),
        )
        for m in matches:
            assert m.evidence or m.assumption
