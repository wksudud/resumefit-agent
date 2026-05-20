"""Unit tests for role tendency scoring module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schemas import RoleTendencyInput
from src.role_tendency import score_role_tendency, build_sample_questionnaire, ROLE_DEFINITIONS


def test_build_sample_questionnaire():
    q = build_sample_questionnaire()
    assert isinstance(q, RoleTendencyInput)
    assert len(q.personality_style) > 0
    assert len(q.courses_learned) > 0
    assert len(q.interests) > 0
    assert len(q.preferred_work_modes) > 0
    assert len(q.work_opinions) > 0
    assert len(q.disliked_tasks) > 0


def test_score_role_tendency_returns_all_roles():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    assert len(result.ranked_roles) == len(ROLE_DEFINITIONS)
    assert result.disclaimer != ""


def test_score_role_tendency_sorted_descending():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    scores = [r.score for r in result.ranked_roles]
    assert scores == sorted(scores, reverse=True), f"Expected descending scores, got {scores}"


def test_score_role_tendency_top_role_has_max_score():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    top = result.ranked_roles[0]
    for role in result.ranked_roles[1:]:
        assert top.score >= role.score


def test_score_role_tendency_all_scores_in_range():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    for role in result.ranked_roles:
        assert 0 <= role.score <= 100, f"{role.role_name_en} score {role.score} out of range"


def test_score_role_tendency_each_role_has_outputs():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    for role in result.ranked_roles:
        assert role.role_name_en
        assert role.role_name_zh
        assert isinstance(role.rationale, list)
        assert isinstance(role.matched_signals, list)
        assert isinstance(role.caution_signals, list)
        assert isinstance(role.next_proof_actions, list)
        assert len(role.next_proof_actions) >= 1


def test_empty_input_still_returns_results():
    empty = RoleTendencyInput()
    result = score_role_tendency(empty)
    assert len(result.ranked_roles) == len(ROLE_DEFINITIONS)
    for role in result.ranked_roles:
        assert 0 <= role.score <= 100


def test_builder_profile_scores_agent_developer_high():
    """A strong builder/engineering profile should score high on agent/full-stack roles."""
    q = RoleTendencyInput(
        personality_style=["builder", "systems thinker", "autonomous", "hands-on"],
        courses_learned=["langchain", "agent orchestration", "multi-agent systems", "python", "docker"],
        interests=["autonomous systems", "agent architecture", "building things that act"],
        disliked_tasks=["writing long documentation"],
        preferred_work_modes=["building/implementing", "engineering", "autonomy"],
        work_opinions=["implementation", "engineering", "automation"],
    )
    result = score_role_tendency(q)
    top = result.ranked_roles[0]
    assert top.role_name_en in (
        "AI Agent Application Developer",
        "Full Stack AI Application Engineer",
        "AI Workflow Automation Engineer",
    ), f"Expected builder profile top role to be agent/full-stack/automation, got {top.role_name_en}"
    assert top.score >= 40, f"Builder profile should score >=40, got {top.score}"


def test_input_summary_preserved():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    assert "personality_style" in result.input_summary
    assert result.input_summary["personality_style"] == q.personality_style


def test_result_to_dict():
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    d = result.to_dict()
    assert "ranked_roles" in d
    assert "input_summary" in d
    assert "disclaimer" in d
    assert "disclaimer_zh" in d
    assert len(d["ranked_roles"]) == len(ROLE_DEFINITIONS)
    role0 = d["ranked_roles"][0]
    assert "role_name_en" in role0
    assert "score" in role0
    assert "rationale" in role0


# ── Edge case / hardening tests ──────────────────────────────────────────────


def test_sparse_input_not_overconfident():
    """A single filled field should not produce a score >= 50."""
    sparse = RoleTendencyInput(
        courses_learned=["python", "docker"],
    )
    result = score_role_tendency(sparse)
    for role in result.ranked_roles:
        assert role.score < 50, (
            f"sparse input (2 courses) gave {role.role_name_en} score={role.score}; "
            f"expected <50 to avoid overconfidence"
        )


def test_minimal_input_all_scores_low():
    """Minimal keyword overlap should keep scores modest (<40)."""
    minimal = RoleTendencyInput(
        personality_style=["builder"],
        courses_learned=["langchain"],
    )
    result = score_role_tendency(minimal)
    assert result.ranked_roles[0].score < 40, (
        f"top role with minimal input scored {result.ranked_roles[0].score}; expected <40"
    )


def test_empty_input_scores_zero_or_near_zero():
    """Completely empty input should score 0 for all roles."""
    empty = RoleTendencyInput()
    result = score_role_tendency(empty)
    for role in result.ranked_roles:
        assert role.score <= 5, (
            f"empty input gave {role.role_name_en} score={role.score}; expected 0-5"
        )


def test_all_role_definitions_have_en_and_zh_names():
    """Every role definition must have both English and Chinese names."""
    for role_def in ROLE_DEFINITIONS:
        assert role_def["role_name_en"], f"Missing role_name_en in {role_def}"
        assert role_def["role_name_zh"], f"Missing role_name_zh in {role_def}"
        assert len(role_def["personality_kw"]) > 0
        assert len(role_def["course_kw"]) > 0
        assert len(role_def["dislike_penalty_kw"]) > 0


def test_disclaimers_not_empty():
    """Both English and Chinese disclaimers must be present."""
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    assert len(result.disclaimer) > 50, "English disclaimer too short or empty"
    assert len(result.disclaimer_zh) > 10, "Chinese disclaimer too short or empty"


def test_backward_compat_resume_fit_inputs():
    """RoleTendencyInput can be stored in ResumeFitInputs."""
    from src.schemas import ResumeFitInputs
    ti = build_sample_questionnaire()
    inputs = ResumeFitInputs(
        resume_text="test resume",
        jd_text="test jd",
        github_profile_path="data/github_profile.json",
        repo_docs_dir="data/repositories",
        role_tendency_input=ti,
    )
    assert inputs.role_tendency_input is ti
    d = inputs.to_dict()
    assert "role_tendency_input" in d
    assert d["role_tendency_input"]["personality_style"] == ti.personality_style


def test_backward_compat_resume_fit_result():
    """RoleTendencyResult can be stored in ResumeFitResult."""
    from src.schemas import ResumeFitResult, ResumeProfile, JobProfile, FitReport
    from src.schemas import PortfolioCopy, VerifierReport
    q = build_sample_questionnaire()
    rt = score_role_tendency(q)
    r = ResumeFitResult(
        resume=ResumeProfile("Test", "Role", [], [], [], []),
        job=JobProfile("Test", "", [], [], [], "", [], []),
        evidence_items=[],
        fit_report=FitReport(0, "", {}, [], 0, 0, 0, [], ""),
        rewrite_suggestions=[],
        skill_gaps=[],
        interview_questions=[],
        portfolio_copy=PortfolioCopy("", "", [], ""),
        workflow_trace=[],
        verifier_report=VerifierReport(0, 0, 0, 0, [], True),
        constraints=[],
        role_tendency=rt,
    )
    assert r.role_tendency is rt
    d = r.to_dict()
    assert "role_tendency" in d
    assert d["role_tendency"]["disclaimer"] == rt.disclaimer


def test_backward_compat_result_without_tendency():
    """ResumeFitResult without role_tendency does not include the key."""
    from src.schemas import ResumeFitResult, ResumeProfile, JobProfile, FitReport
    from src.schemas import PortfolioCopy, VerifierReport
    r = ResumeFitResult(
        resume=ResumeProfile("Test", "Role", [], [], [], []),
        job=JobProfile("Test", "", [], [], [], "", [], []),
        evidence_items=[],
        fit_report=FitReport(0, "", {}, [], 0, 0, 0, [], ""),
        rewrite_suggestions=[],
        skill_gaps=[],
        interview_questions=[],
        portfolio_copy=PortfolioCopy("", "", [], ""),
        workflow_trace=[],
        verifier_report=VerifierReport(0, 0, 0, 0, [], True),
        constraints=[],
        role_tendency=None,
    )
    d = r.to_dict()
    assert "role_tendency" not in d


def test_score_role_tendency_disclaimer_includes_heuristic_guidance():
    """Disclaimer must signal heuristic nature, not psychological diagnosis."""
    q = build_sample_questionnaire()
    result = score_role_tendency(q)
    assert "heuristic" in result.disclaimer.lower()
    assert "not" in result.disclaimer.lower()
    assert "psychological" in result.disclaimer.lower() or "diagnosis" in result.disclaimer.lower()


def test_report_includes_chinese_localization_note():
    """Report must include a Chinese note about English demo content in role details."""
    from src.schemas import ResumeFitResult, ResumeProfile, JobProfile, FitReport
    from src.schemas import PortfolioCopy, VerifierReport
    from src.report_writer import render_report_text

    q = build_sample_questionnaire()
    rt = score_role_tendency(q)
    r = ResumeFitResult(
        resume=ResumeProfile("Test", "Role", [], [], [], []),
        job=JobProfile("Test", "", [], [], [], "", [], []),
        evidence_items=[],
        fit_report=FitReport(0, "", {}, [], 0, 0, 0, [], ""),
        rewrite_suggestions=[],
        skill_gaps=[],
        interview_questions=[],
        portfolio_copy=PortfolioCopy("", "", [], ""),
        workflow_trace=[],
        verifier_report=VerifierReport(0, 0, 0, 0, [], True),
        constraints=[],
        role_tendency=rt,
    )
    report = render_report_text(r)
    # Chinese localization note must be present
    assert "详细分析内容" in report, "Report missing Chinese localization note for role details"
    assert "英文演示文本" in report, "Report missing Chinese note about English demo text"
    # Chinese section labels must be present alongside English
    assert "匹配信号" in report, "Report missing Chinese section label for matched signals"
    assert "注意事项" in report, "Report missing Chinese section label for cautions"
    assert "评分理由" in report, "Report missing Chinese section label for rationale"
    assert "下一步证明行动" in report, "Report missing Chinese section label for next actions"
