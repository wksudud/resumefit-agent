"""Integration tests for agent_workflow module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schemas import ResumeFitInputs, ResumeFitResult, WorkflowStep, RoleTendencyInput
from src.agent_workflow import run_resume_fit_workflow
from src.role_tendency import build_sample_questionnaire


SAMPLE_RESUME = """## Contact
- **Name**: Test User
- **Target Role**: AI Agent Engineer

## Education
- BUPT, B.Eng. CS

## Skills
- Python, Git, LLM APIs, Streamlit, Prompt Engineering

## Projects

### Test Agent
An AI agent workflow project.
- Built multi-agent pipeline
- Technologies: Python, Streamlit

## Achievements
- Built an agent project

## Constraints
- No internship
"""

SAMPLE_JD = """## Position
**AI Agent Engineer** (Junior)

## Responsibilities
- Design agent workflows
- Build LLM-powered applications

## Required Skills
- Python
- LLM APIs
- Agent architecture design

## Preferred Skills
- Streamlit
- Docker

## Seniority
Junior / Intern level
"""


class TestWorkflow:
    def test_runs_with_sample_data(self, tmp_path):
        # Write temp files
        import json
        profile_path = tmp_path / "github_profile.json"
        profile_path.write_text(json.dumps({
            "repositories": [
                {
                    "name": "test-agent",
                    "description": "Test agent project",
                    "language": "Python",
                    "topics": ["ai-agent", "streamlit"],
                    "stars": 0,
                    "forks": 0,
                    "is_public": True,
                    "has_readme": True,
                    "has_tests": True,
                    "commit_count": 15,
                },
            ],
        }))

        repo_dir = tmp_path / "repos"
        repo_dir.mkdir()
        (repo_dir / "test_agent.md").write_text("Test agent repo doc")

        inputs = ResumeFitInputs(
            resume_text=SAMPLE_RESUME,
            jd_text=SAMPLE_JD,
            github_profile_path=str(profile_path),
            repo_docs_dir=str(repo_dir),
        )

        result = run_resume_fit_workflow(inputs)
        assert isinstance(result, ResumeFitResult)
        assert result.fit_report.overall_score > 0
        assert len(result.workflow_trace) >= 7
        assert result.verifier_report.total_claims > 0

    def test_workflow_trace_complete(self, tmp_path):
        import json
        profile_path = tmp_path / "github_profile.json"
        profile_path.write_text(json.dumps({"repositories": []}))
        repo_dir = tmp_path / "repos"
        repo_dir.mkdir()

        inputs = ResumeFitInputs(
            resume_text=SAMPLE_RESUME,
            jd_text=SAMPLE_JD,
            github_profile_path=str(profile_path),
            repo_docs_dir=str(repo_dir),
        )
        result = run_resume_fit_workflow(inputs)

        # Check all expected agents in trace
        agents = {step.agent for step in result.workflow_trace}
        expected = {"Resume Parser", "JD Analyzer", "GitHub Evidence Agent",
                     "Fit Scoring Agent", "Skill Gap Agent", "Verifier"}
        assert expected.issubset(agents)

    def test_errors_captured(self, tmp_path):
        inputs = ResumeFitInputs(
            resume_text=SAMPLE_RESUME,
            jd_text=SAMPLE_JD,
            github_profile_path=str(tmp_path / "nonexistent.json"),
            repo_docs_dir=str(tmp_path / "nonexistent"),
        )
        result = run_resume_fit_workflow(inputs)
        # Should either error or complete with gaps
        assert isinstance(result, ResumeFitResult)

    def test_role_tendency_input_none_gives_no_tendency(self, tmp_path):
        """When role_tendency_input=None, result.role_tendency must be None."""
        import json
        profile_path = tmp_path / "github_profile.json"
        profile_path.write_text(json.dumps({"repositories": []}))
        repo_dir = tmp_path / "repos"
        repo_dir.mkdir()

        inputs = ResumeFitInputs(
            resume_text=SAMPLE_RESUME,
            jd_text=SAMPLE_JD,
            github_profile_path=str(profile_path),
            repo_docs_dir=str(repo_dir),
            role_tendency_input=None,
        )
        result = run_resume_fit_workflow(inputs)
        assert result.role_tendency is None, (
            f"Expected role_tendency=None when no input provided, got {type(result.role_tendency)}"
        )

    def test_explicit_sample_questionnaire_produces_tendency(self, tmp_path):
        """Explicit sample questionnaire must produce role tendency for demo use."""
        import json
        profile_path = tmp_path / "github_profile.json"
        profile_path.write_text(json.dumps({"repositories": []}))
        repo_dir = tmp_path / "repos"
        repo_dir.mkdir()

        sample_q = build_sample_questionnaire()
        inputs = ResumeFitInputs(
            resume_text=SAMPLE_RESUME,
            jd_text=SAMPLE_JD,
            github_profile_path=str(profile_path),
            repo_docs_dir=str(repo_dir),
            role_tendency_input=sample_q,
        )
        result = run_resume_fit_workflow(inputs)
        assert result.role_tendency is not None, (
            "Expected role_tendency when explicit sample questionnaire provided"
        )
        assert len(result.role_tendency.ranked_roles) > 0, (
            "Expected non-empty ranked_roles from explicit sample questionnaire"
        )
        top = result.role_tendency.ranked_roles[0]
        assert 0 <= top.score <= 100
