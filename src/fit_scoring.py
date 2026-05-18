"""Apply scoring rubric to produce a FitReport."""

from __future__ import annotations

from src.schemas import (
    ResumeProfile,
    JobProfile,
    ProjectEvidence,
    FitReport,
    JDRequirementMatch,
)

W_ROLE = 0.25
W_SKILL = 0.25
W_PROJECT = 0.25
W_GITHUB = 0.15
W_RISK = 0.10


def _label(score: int) -> str:
    if score >= 80:
        return "strong match with clear evidence"
    elif score >= 60:
        return "plausible match with targeted rewrite and proof gaps"
    elif score >= 40:
        return "partial match; needs focused artifact building"
    else:
        return "not recommended without major repositioning"


def score_fit(
    resume: ResumeProfile,
    job: JobProfile,
    evidence_items: list[ProjectEvidence],
) -> FitReport:
    role_score = _score_role_alignment(resume, job)
    skill_score = _score_skill_match(resume, job)
    project_score = _score_project_evidence(evidence_items)
    github_score = _score_github_proof(evidence_items)
    risk_score = _score_risk_honesty(resume, job)

    overall = int(
        role_score * W_ROLE
        + skill_score * W_SKILL
        + project_score * W_PROJECT
        + github_score * W_GITHUB
        + risk_score * W_RISK
    )

    all_requirements = _build_requirement_list(job)
    matches = _match_requirements(all_requirements, resume, evidence_items)

    matched = [m for m in matches if m.status == "matched"]
    partial = [m for m in matches if m.status == "partial"]
    gaps = [m for m in matches if m.status == "gap"]

    risks = _identify_risks(resume, job, evidence_items)

    return FitReport(
        overall_score=overall,
        score_label=_label(overall),
        dimension_scores={
            "role_alignment": round(role_score, 1),
            "core_skill_match": round(skill_score, 1),
            "project_evidence": round(project_score, 1),
            "github_proof": round(github_score, 1),
            "risk_honesty": round(risk_score, 1),
        },
        requirement_matches=matches,
        matched_count=len(matched),
        partial_count=len(partial),
        gap_count=len(gaps),
        risks=risks,
        suggestions_summary=_suggestions_summary(matched, partial, gaps),
    )


def _score_role_alignment(resume: ResumeProfile, job: JobProfile) -> float:
    score = 60.0
    jd_title = job.title.lower()
    resume_target = resume.target_role.lower()
    role_kw = ["ai agent", "llm application", "aiops", "ai product", "ai engineer"]
    for kw in role_kw:
        if kw in jd_title and any(kw_part in resume_target for kw_part in kw.split()):
            score += 10
            break
    if "junior" in job.seniority_signal.lower() or "intern" in job.seniority_signal.lower():
        score += 10
    if "entry" in job.seniority_signal.lower():
        score += 5
    resp_text = " ".join(job.responsibilities).lower()
    if any(kw in resp_text for kw in ["agent", "llm", "ai"]):
        if any(kw in resume_target for kw in ["agent", "llm", "ai"]):
            score += 10
    has_pure_ml = any(kw in " ".join(resume.skills).lower() for kw in ["model training", "deep learning research"])
    has_no_app = not resume.projects
    red_flag_text = " ".join(job.red_flags).lower()
    if "model training" in red_flag_text and not has_pure_ml:
        score += 5
    if "no evidence" in red_flag_text and not has_no_app:
        score += 5
    return min(score, 100)


def _score_skill_match(resume: ResumeProfile, job: JobProfile) -> float:
    resume_skills_lower = [s.lower() for s in resume.skills]
    skill_text = " ".join(resume_skills_lower)
    required = job.required_skills
    preferred = job.preferred_skills
    req_matched = 0.0
    for skill_text_req in required:
        skill_lower = skill_text_req.lower()
        if any(kw in skill_text for kw in _skill_keywords(skill_lower)):
            req_matched += 1.0
        elif any(kw in skill_lower for kw in skill_text.split()):
            req_matched += 0.5
    pref_matched = 0.0
    for skill_text_pref in preferred:
        skill_lower = skill_text_pref.lower()
        if any(kw in skill_text for kw in _skill_keywords(skill_lower)):
            pref_matched += 1.0
        elif any(kw in skill_lower for kw in skill_text.split()):
            pref_matched += 0.5
    req_ratio = req_matched / max(len(required), 1)
    pref_ratio = pref_matched / max(len(preferred), 1)
    score = int(req_ratio * 60 + pref_ratio * 40)
    return min(score, 100)


def _skill_keywords(skill_text: str) -> list[str]:
    kws = [skill_text]
    kw_map = {
        "python": ["python"],
        "pandas": ["pandas", "data"],
        "numpy": ["numpy", "data"],
        "llm": ["llm", "openai", "gpt", "prompt"],
        "prompt engineering": ["prompt"],
        "agent": ["agent", "workflow", "orchestrat"],
        "rag": ["rag", "retrieval", "vector", "embedding"],
        "streamlit": ["streamlit"],
        "git": ["git"],
        "docker": ["docker"],
        "evaluation": ["eval", "metric", "quality"],
        "documentation": ["document", "readme"],
        "domain": ["telecom", "network", "domain"],
    }
    for key, values in kw_map.items():
        if key in skill_text:
            kws.extend(values)
    return kws


def _score_project_evidence(evidence_items: list[ProjectEvidence]) -> float:
    if not evidence_items:
        return 20
    scores: list[float] = []
    for e in evidence_items:
        s = 40.0
        if e.technologies:
            s += min(len(e.technologies) * 3, 15)
        if e.agent_llm_aiops_signals:
            s += min(len(e.agent_llm_aiops_signals) * 5, 25)
        if e.measurable_proof:
            s += min(len(e.measurable_proof) * 4, 20)
        s -= len(e.weak_evidence_warnings) * 5
        scores.append(max(s, 10))
    if len(scores) == 1:
        return min(scores[0], 100)
    elif len(scores) == 2:
        return min(scores[0] * 0.6 + scores[1] * 0.4, 100)
    else:
        return min(scores[0] * 0.5 + scores[1] * 0.3 + sum(scores[2:]) / len(scores[2:]) * 0.2, 100)


def _score_github_proof(evidence_items: list[ProjectEvidence]) -> float:
    if not evidence_items:
        return 20
    scores: list[float] = []
    for e in evidence_items:
        s = 30.0
        warnings_lower = [w.lower() for w in e.weak_evidence_warnings]
        if not any("no readme" in w for w in warnings_lower):
            s += 20
        if not any("no tests" in w for w in warnings_lower):
            s += 15
        if not any("not public" in w for w in warnings_lower):
            s += 20
        if not any("very few commits" in w for w in warnings_lower):
            s += 10
        if not any("no community" in w for w in warnings_lower):
            s += 5
        scores.append(s)
    return min(sum(scores) / len(scores), 100)


def _score_risk_honesty(resume: ResumeProfile, job: JobProfile) -> float:
    score = 70.0
    if resume.constraints:
        score += 15
    red_flag_text = " ".join(job.red_flags).lower()
    resume_text = " ".join(resume.skills + resume.achievements).lower()
    red_flag_triggered = False
    if "model training" in red_flag_text and "model training" in resume_text:
        red_flag_triggered = True
    if "api calls without" in red_flag_text and not resume.projects:
        red_flag_triggered = True
    if not red_flag_triggered:
        score += 10
    score += 5
    return min(score, 100)


def _build_requirement_list(job: JobProfile) -> list[dict]:
    reqs: list[dict] = []
    for r in job.required_skills:
        reqs.append({"text": r, "category": "skill", "importance": "required"})
    for p in job.preferred_skills:
        reqs.append({"text": p, "category": "skill", "importance": "preferred"})
    for r in job.responsibilities:
        reqs.append({"text": r, "category": "responsibility", "importance": "required"})
    return reqs


def _match_requirements(
    reqs: list[dict],
    resume: ResumeProfile,
    evidence_items: list[ProjectEvidence],
) -> list[JDRequirementMatch]:
    matches: list[JDRequirementMatch] = []

    all_skills_text = " ".join(resume.skills).lower()
    all_projects_text = " ".join(
        p.description + " " + " ".join(p.highlights)
        for p in resume.projects
    ).lower()
    all_evidence_text = " ".join(
        " ".join(e.agent_llm_aiops_signals) + " " + " ".join(e.measurable_proof)
        for e in evidence_items
    ).lower()
    combined = all_skills_text + " " + all_projects_text + " " + all_evidence_text

    stop = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "with",
            "and", "or", "is", "are", "be", "has", "have", "can", "may",
            "basic", "experience", "knowledge", "understanding", "familiarity"}

    for req in reqs:
        text = req["text"].lower()
        importance = req["importance"]
        keywords = set(text.replace(",", " ").replace("/", " ").split())
        keywords -= stop
        matched_kw = [kw for kw in keywords if kw in combined]

        evidence_list: list[str] = []
        assumption = False

        if len(matched_kw) >= len(keywords) * 0.5:
            status = "matched"
            evidence_list = [
                f"Keyword match: {kw!r} found in resume or project evidence"
                for kw in matched_kw[:3]
            ]
        elif len(matched_kw) >= 1:
            status = "partial"
            evidence_list = [
                f"Partial keyword match: {kw!r} found"
                for kw in matched_kw[:3]
            ]
            if len(matched_kw) < len(keywords) * 0.3:
                assumption = True
        else:
            if importance == "required":
                status = "gap"
                assumption = True
                evidence_list = ["No matching signal found in resume or project evidence"]
            else:
                status = "partial"
                assumption = True
                evidence_list = ["Preferred skill - assumed acquirable based on adjacent skills"]

        warning = ""
        if assumption:
            warning = "Assumption-based match - needs verification with real project evidence"

        matches.append(JDRequirementMatch(
            requirement=req["text"],
            status=status,
            evidence=evidence_list,
            assumption=assumption,
            warning=warning,
        ))

    return matches


def _identify_risks(
    resume: ResumeProfile,
    job: JobProfile,
    evidence_items: list[ProjectEvidence],
) -> list[str]:
    risks: list[str] = []
    if not resume.projects:
        risks.append("No project evidence available - all claims are self-reported")
    public_repos = sum(1 for e in evidence_items if not any(
        "not public" in w.lower() for w in e.weak_evidence_warnings
    ))
    if public_repos == 0:
        risks.append("No public GitHub repositories - employer cannot verify project claims independently")
    if resume.constraints:
        risks.append(
            f"Candidate self-reports {len(resume.constraints)} constraints - "
            "review for interview discussion"
        )
    total_warnings = sum(len(e.weak_evidence_warnings) for e in evidence_items)
    if total_warnings >= 5:
        risks.append(
            f"Multiple evidence warnings ({total_warnings}) - "
            "project proof quality needs improvement"
        )
    strong_ai_projects = sum(
        1 for e in evidence_items if len(e.agent_llm_aiops_signals) >= 5
    )
    if strong_ai_projects < 2:
        risks.append(
            "Limited number of strong AI/Agent project signals - "
            "consider building additional portfolio projects"
        )
    return risks


def _suggestions_summary(
    matched: list[JDRequirementMatch],
    partial: list[JDRequirementMatch],
    gaps: list[JDRequirementMatch],
) -> str:
    parts = []
    if matched:
        parts.append(f"{len(matched)} requirements strongly matched")
    if partial:
        parts.append(f"{len(partial)} requirements partially matched")
    if gaps:
        parts.append(f"{len(gaps)} gaps identified")
    if not parts:
        return "No requirements analyzed"
    return "; ".join(parts) + "."
