"""Generate interview follow-up questions from fit analysis gaps."""

from __future__ import annotations

from src.schemas import (
    FitReport,
    ResumeProfile,
    ProjectEvidence,
    InterviewQuestion,
    JDRequirementMatch,
)


def generate_interview_questions(
    fit_report: FitReport,
    resume: ResumeProfile | None = None,
    evidence_items: list[ProjectEvidence] | None = None,
) -> list[InterviewQuestion]:
    questions: list[InterviewQuestion] = []

    gaps = [m for m in fit_report.requirement_matches if m.status == "gap"]
    partials = [m for m in fit_report.requirement_matches if m.status == "partial"]

    for gap in gaps[:4]:
        questions.append(InterviewQuestion(
            question=_gap_question(gap),
            category="skill-gap",
            target_weakness=gap.requirement,
            suggested_angle=_gap_angle(gap),
        ))

    for partial in partials[:3]:
        questions.append(InterviewQuestion(
            question=_partial_question(partial),
            category="project-detail",
            target_weakness=partial.requirement,
            suggested_angle=_partial_angle(partial),
        ))

    questions.extend(_scenario_questions(fit_report))

    if resume and resume.projects:
        questions.append(InterviewQuestion(
            question=f"Walk me through the architecture of {resume.projects[0].name}. "
                     f"What were the key design decisions and what would you do differently?",
            category="project-deep-dive",
            target_weakness="Project depth unverified",
            suggested_angle="Show system design thinking, trade-off reasoning, and honest reflection on limitations",
        ))

    if resume and len(resume.projects) >= 2:
        questions.append(InterviewQuestion(
            question="How would you compare your two main projects in terms of agent "
                     "architecture decisions? What pattern did each use and why?",
            category="architecture",
            target_weakness="Cross-project architectural reasoning",
            suggested_angle="Demonstrate ability to abstract patterns and make intentional design choices",
        ))

    return questions


def _gap_question(gap: JDRequirementMatch) -> str:
    req = gap.requirement.rstrip(".")
    return (
        f"This role requires {req}. Can you describe any experience you have "
        f"with this, even from coursework or self-study?"
    )


def _gap_angle(gap: JDRequirementMatch) -> str:
    return (
        "Acknowledge the gap honestly, then pivot to adjacent experience "
        "and concrete plans to build the skill. Show learning agility."
    )


def _partial_question(partial: JDRequirementMatch) -> str:
    req = partial.requirement.rstrip(".")
    return (
        f"Your resume shows some experience with {req}. Can you give a "
        f"specific example of how you applied it in a project?"
    )


def _partial_angle(partial: JDRequirementMatch) -> str:
    return (
        "Provide a concrete before/after or problem/solution story. "
        "Include measurable outcome if available, or state scope clearly."
    )


def _scenario_questions(fit_report: FitReport) -> list[InterviewQuestion]:
    questions: list[InterviewQuestion] = []
    if fit_report.gap_count >= 3:
        questions.append(InterviewQuestion(
            question="Imagine you join the team and discover a key service lacks "
                     "any evaluation framework for its LLM outputs. How would you "
                     "approach building one from scratch?",
            category="scenario",
            target_weakness="Evaluation/metrics gap",
            suggested_angle="Show systematic thinking: define success criteria, "
                           "build minimal eval harness, iterate with real data",
        ))
    if any("github" in r.requirement.lower() or "public" in r.requirement.lower()
           for r in fit_report.requirement_matches):
        questions.append(InterviewQuestion(
            question="If you were to open-source one of your projects tomorrow, "
                     "what would you improve first before making it public?",
            category="scenario",
            target_weakness="Public project readiness",
            suggested_angle="Demonstrate awareness of documentation, testing, "
                           "and onboarding as engineering quality signals",
        ))
    return questions
