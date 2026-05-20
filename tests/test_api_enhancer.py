import json
from unittest.mock import patch

from src.api_enhancer import enhance_with_api
from src.schemas import (
    FitReport,
    InterviewQuestion,
    JobProfile,
    PortfolioCopy,
    ResumeFitResult,
    ResumeProfile,
    RewriteSuggestion,
    VerifierReport,
)


def _result():
    return ResumeFitResult(
        resume=ResumeProfile("Test User", "AI Engineer", [], [], [], []),
        job=JobProfile("AI Engineer", "", [], [], [], ""),
        evidence_items=[],
        fit_report=FitReport(80, "strong", {}, [], 0, 0, 0, [], ""),
        rewrite_suggestions=[
            RewriteSuggestion("Project", "Agent workflow", "Built tool", "Built workflow", "README", "evidence-backed")
        ],
        skill_gaps=[],
        interview_questions=[
            InterviewQuestion("Explain the project.", "project-detail", "depth", "Use a concrete story.")
        ],
        portfolio_copy=PortfolioCopy("card", "tagline", ["bullet"], "story"),
        workflow_trace=[],
        verifier_report=VerifierReport(0, 0, 0, 0, [], True),
        constraints=[],
    )


def test_api_mode_without_key_falls_back_to_offline():
    result = enhance_with_api(_result(), "", "https://api.openai.com/v1", "gpt-4o-mini")

    assert result.generation_mode == "offline"
    assert "no API key" in result.errors[0]


def test_api_mode_applies_structured_response():
    response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "rewrite_suggestions": [
                            {
                                "source_project": "Project",
                                "target_jd_requirement": "Agent workflow",
                                "before_text": "Built tool",
                                "after_text": "Built an evidence-grounded agent workflow.",
                                "evidence": "README",
                                "honesty_note": "evidence-backed",
                            }
                        ],
                        "interview_questions": [
                            {
                                "question": "How did you design the workflow?",
                                "category": "project-detail",
                                "target_weakness": "depth",
                                "suggested_angle": "Explain trade-offs and evidence.",
                            }
                        ],
                        "portfolio_copy": {
                            "short_card": "enhanced card",
                            "readme_tagline": "enhanced tagline",
                            "resume_bullets": ["enhanced bullet"],
                            "project_story": "enhanced story",
                        },
                    })
                }
            }
        ]
    }

    class FakeHTTPResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(response).encode("utf-8")

    with patch("src.api_enhancer.request.urlopen", lambda req, timeout: FakeHTTPResponse()):
        result = enhance_with_api(_result(), "test-key", "https://example.com/v1", "test-model")

    assert result.generation_mode == "api"
    assert result.rewrite_suggestions[0].after_text == "Built an evidence-grounded agent workflow."
    assert result.interview_questions[0].question == "How did you design the workflow?"
    assert result.portfolio_copy.short_card == "enhanced card"
    assert result.workflow_trace[-1].agent == "API Enhancement Agent"
