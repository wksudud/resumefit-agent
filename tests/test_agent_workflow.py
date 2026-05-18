"""Integration tests for agent_workflow module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schemas import ResumeFitInputs, ResumeFitResult, WorkflowStep
from src.agent_workflow import run_resume_fit_workflow


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
