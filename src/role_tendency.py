"""Deterministic role tendency scoring from self-reported questionnaire inputs."""

from __future__ import annotations

from src.schemas import RoleTendencyInput, RoleTendencyResult, RoleTendencyScore


ROLE_DEFINITIONS: list[dict] = [
    {
        "role_name_en": "AI Agent Application Developer",
        "role_name_zh": "AI Agent 应用开发工程师",
        "personality_kw": [
            "builder", "systems thinker", "autonomous", "self-directed",
            "experimenter", "pragmatic", "curious about how things work",
        ],
        "course_kw": [
            "agent", "multi-agent", "langchain", "langgraph", "crewai",
            "autogen", "orchestration", "tool calling", "function calling",
            "reinforcement learning", "planning", "reasoning",
        ],
        "interest_kw": [
            "autonomous systems", "agent architecture", "multi-agent",
            "tool use", "decision making", "orchestration",
            "building things that act", "intelligent automation",
        ],
        "work_mode_kw": [
            "building/implementing", "engineering", "autonomy",
            "hands-on coding", "systems design",
        ],
        "opinion_kw": [
            "implementation", "engineering", "building",
            "systems", "automation",
        ],
        "dislike_penalty_kw": [
            "coding", "implementation", "engineering", "building",
        ],
    },
    {
        "role_name_en": "LLM Application Engineer",
        "role_name_zh": "LLM 应用工程师",
        "personality_kw": [
            "hands-on", "detail-oriented", "experimenter", "tinkerer",
            "pragmatic", "prompt crafter", "evaluation-focused",
        ],
        "course_kw": [
            "prompt engineering", "llm", "gpt", "openai", "rag",
            "retrieval", "embedding", "vector database", "fine-tuning",
            "langchain", "llamaindex", "token", "transformer",
            "nlp", "natural language",
        ],
        "interest_kw": [
            "prompt engineering", "llm behavior", "model capabilities",
            "rag", "retrieval", "text generation", "nlp",
            "language models", "evaluation", "benchmarking",
        ],
        "work_mode_kw": [
            "building/implementing", "engineering", "research",
            "experimentation", "analysis",
        ],
        "opinion_kw": [
            "implementation", "engineering", "analysis",
            "communication",
        ],
        "dislike_penalty_kw": [
            "coding", "implementation", "engineering",
        ],
    },
    {
        "role_name_en": "AI Product Engineer",
        "role_name_zh": "AI 产品工程师",
        "personality_kw": [
            "product thinker", "user empathy", "business-aware",
            "creative", "collaborative", "outcome-driven",
            "design-sensitive",
        ],
        "course_kw": [
            "product management", "ux", "user research", "design thinking",
            "prototyping", "mvp", "a/b testing", "metrics",
            "ai product", "llm application",
        ],
        "interest_kw": [
            "user experience", "product design", "ai applications",
            "user needs", "business impact", "product-market fit",
            "prototyping", "iteration",
        ],
        "work_mode_kw": [
            "product thinking", "collaboration", "communication",
            "design", "business impact", "user research",
        ],
        "opinion_kw": [
            "design", "business impact", "communication",
            "product", "user",
        ],
        "dislike_penalty_kw": [
            "product", "user", "design", "business",
        ],
    },
    {
        "role_name_en": "AIOps Intelligent Operations Engineer",
        "role_name_zh": "AIOps 智能运维工程师",
        "personality_kw": [
            "systems thinker", "stability-oriented", "detail-oriented",
            "calm under pressure", "monitoring-minded", "incident responder",
        ],
        "course_kw": [
            "devops", "monitoring", "observability", "incident management",
            "sre", "kubernetes", "docker", "infrastructure",
            "aiops", "anomaly detection", "log analysis",
            "alerting", "automation", "ci/cd",
        ],
        "interest_kw": [
            "system reliability", "monitoring", "automation",
            "incident response", "infrastructure", "observability",
            "root cause analysis", "operations",
        ],
        "work_mode_kw": [
            "operations", "stability", "analysis", "engineering",
            "autonomy", "building/implementing",
        ],
        "opinion_kw": [
            "operations", "analysis", "implementation",
            "engineering",
        ],
        "dislike_penalty_kw": [
            "operations", "monitoring", "infrastructure",
            "on-call", "incidents",
        ],
    },
    {
        "role_name_en": "AI Workflow Automation Engineer",
        "role_name_zh": "AI 工作流自动化工程师",
        "personality_kw": [
            "efficiency-driven", "process-oriented", "pragmatic",
            "builder", "integration-focused", "tool-adept",
        ],
        "course_kw": [
            "workflow", "automation", "n8n", "zapier", "make",
            "integration", "api", "low-code", "no-code",
            "langchain", "pipeline", "etl", "orchestration",
        ],
        "interest_kw": [
            "automation", "workflow", "process optimization",
            "integration", "efficiency", "tool chaining",
            "low-code", "no-code",
        ],
        "work_mode_kw": [
            "building/implementing", "automation", "engineering",
            "operations", "hands-on coding",
        ],
        "opinion_kw": [
            "implementation", "automation", "operations",
            "engineering",
        ],
        "dislike_penalty_kw": [
            "automation", "integration", "workflow",
        ],
    },
    {
        "role_name_en": "Full Stack AI Application Engineer",
        "role_name_zh": "全栈 AI 应用工程师",
        "personality_kw": [
            "versatile", "full-stack", "builder", "end-to-end thinker",
            "ui-aware", "collaborative", "self-directed",
        ],
        "course_kw": [
            "frontend", "backend", "react", "vue", "fastapi",
            "flask", "database", "api design", "llm", "streamlit",
            "gradio", "deployment", "docker", "cloud",
        ],
        "interest_kw": [
            "full stack", "frontend", "backend", "api design",
            "user interface", "deployment", "end-to-end",
            "building complete products",
        ],
        "work_mode_kw": [
            "building/implementing", "engineering", "design",
            "collaboration", "hands-on coding",
        ],
        "opinion_kw": [
            "implementation", "design", "engineering",
            "communication",
        ],
        "dislike_penalty_kw": [
            "coding", "implementation", "frontend", "backend",
        ],
    },
]

def _keyword_match(texts: list[str], keywords: list[str]) -> int:
    """Count how many keywords appear in any of the texts."""
    combined = " ".join(t.lower() for t in texts)
    return sum(1 for kw in keywords if kw.lower() in combined)


def _keyword_match_count(texts: list[str], keywords: list[str]) -> int:
    """Count total keyword occurrences (allowing duplicates)."""
    combined = " ".join(t.lower() for t in texts)
    count = 0
    for kw in keywords:
        count += combined.count(kw.lower())
    return count


def score_role_tendency(user_input: RoleTendencyInput) -> RoleTendencyResult:
    results: list[RoleTendencyScore] = []

    for role_def in ROLE_DEFINITIONS:
        role_score = 0
        rationale: list[str] = []
        matched_signals: list[str] = []
        caution_signals: list[str] = []

        # 1. Personality / work style alignment (max 25 points)
        pers_matches = _keyword_match(user_input.personality_style, role_def["personality_kw"])
        pers_score = min(pers_matches * 6, 25)
        role_score += pers_score
        if pers_matches > 0:
            matched_signals.append(
                f"Personality signals match: {pers_matches} trait(s) aligned with {role_def['role_name_en']}"
            )
            rationale.append(f"Personality alignment contributed {pers_score}/25")
        else:
            caution_signals.append("No direct personality-style signal match for this role")

        # 2. Courses / knowledge alignment (max 25 points)
        course_matches = _keyword_match_count(user_input.courses_learned, role_def["course_kw"])
        course_score = min(course_matches * 5, 25)
        role_score += course_score
        if course_matches > 0:
            matched_signals.append(
                f"Course/knowledge signals match: {course_matches} topic(s) relevant to {role_def['role_name_en']}"
            )
            rationale.append(f"Course alignment contributed {course_score}/25")
        else:
            caution_signals.append("No course or knowledge signal detected; consider relevant coursework")

        # 3. Interests alignment (max 20 points)
        interest_matches = _keyword_match(user_input.interests, role_def["interest_kw"])
        interest_score = min(interest_matches * 5, 20)
        role_score += interest_score
        if interest_matches > 0:
            matched_signals.append(
                f"Interest signals match: {interest_matches} area(s) relevant to {role_def['role_name_en']}"
            )
            rationale.append(f"Interest alignment contributed {interest_score}/20")
        else:
            caution_signals.append("No explicit interest signal for this role domain")

        # 4. Work mode alignment (max 15 points)
        mode_matches = _keyword_match(user_input.preferred_work_modes, role_def["work_mode_kw"])
        mode_score = min(mode_matches * 5, 15)
        role_score += mode_score
        if mode_matches > 0:
            matched_signals.append(
                f"Work mode signals match: {mode_matches} preference(s) aligned"
            )
            rationale.append(f"Work mode alignment contributed {mode_score}/15")
        else:
            caution_signals.append("Preferred work mode not clearly aligned with this role pattern")

        # 5. Work opinions alignment (max 10 points)
        opinion_matches = _keyword_match(user_input.work_opinions, role_def["opinion_kw"])
        opinion_score = min(opinion_matches * 3, 10)
        role_score += opinion_score
        if opinion_matches > 0:
            matched_signals.append(f"Work opinion signals match: {opinion_matches} item(s) aligned")
            rationale.append(f"Work opinion alignment contributed {opinion_score}/10")

        # 6. Dislike penalties (subtract up to 15 points)
        dislike_matches = _keyword_match(user_input.disliked_tasks, role_def["dislike_penalty_kw"])
        penalty = min(dislike_matches * 5, 15)
        role_score -= penalty
        if dislike_matches > 0:
            caution_signals.append(
                f"Disliked-tasks overlap detected: {dislike_matches} dislike(s) conflict with this role's core activities"
            )
            rationale.append(f"Dislike penalty: -{penalty}/15")

        # Clamp score to 0-100
        role_score = max(0, min(role_score, 100))

        # Generate next proof-building actions
        next_actions = _build_next_actions(role_def, user_input, role_score)

        results.append(RoleTendencyScore(
            role_name_en=role_def["role_name_en"],
            role_name_zh=role_def["role_name_zh"],
            score=role_score,
            rationale=rationale if rationale else ["Insufficient input signals for detailed scoring"],
            matched_signals=matched_signals if matched_signals else ["No strong signal matches found"],
            caution_signals=caution_signals,
            next_proof_actions=next_actions,
        ))

    results.sort(key=lambda r: r.score, reverse=True)

    return RoleTendencyResult(
        ranked_roles=results,
        input_summary={
            "personality_style": user_input.personality_style,
            "courses_learned": user_input.courses_learned,
            "interests": user_input.interests,
            "disliked_tasks": user_input.disliked_tasks,
            "preferred_work_modes": user_input.preferred_work_modes,
            "work_opinions": user_input.work_opinions,
        },
    )


def _build_next_actions(
    role_def: dict,
    user_input: RoleTendencyInput,
    score: int,
) -> list[str]:
    actions: list[str] = []
    role_name = role_def["role_name_en"]

    if score >= 60:
        actions.append(
            f"Find 2-3 {role_name} job descriptions (JDs) and run ResumeFit JD fit scoring "
            f"to identify specific skill and evidence gaps against real requirements."
        )
        actions.append(
            f"Build or extend one project that demonstrates core {role_name} skills "
            f"with public GitHub evidence (README, tests, CI, measurable results)."
        )
    elif score >= 35:
        actions.append(
            f"Take 1-2 courses or build a guided project in {role_name} core topics "
            f"to strengthen knowledge signals before targeting this role."
        )
        actions.append(
            f"Talk to 1-2 practitioners in {role_name} to validate whether the day-to-day "
            f"work matches your interests and work style preferences."
        )
    else:
        actions.append(
            f"Explore adjacent roles before committing to {role_name}. "
            f"Review higher-scoring role recommendations for better alignment."
        )
        actions.append(
            f"If {role_name} still interests you, start with a small exploratory project "
            f"to test genuine fit before deeper investment."
        )

    return actions


def build_sample_questionnaire() -> RoleTendencyInput:
    """Return a default sample questionnaire for demo and testing.

    This represents a candidate who enjoys building and engineering,
    has some AI coursework, and prefers autonomy with product thinking.
    """
    return RoleTendencyInput(
        personality_style=[
            "builder",
            "systems thinker",
            "autonomous",
            "curious about how things work",
            "pragmatic",
        ],
        courses_learned=[
            "prompt engineering",
            "langchain",
            "llm application development",
            "python programming",
            "rag and vector databases",
            "docker basics",
            "fastapi",
            "streamlit",
        ],
        interests=[
            "autonomous systems",
            "agent architecture",
            "building things that act",
            "user experience",
            "automation",
            "full stack development",
        ],
        disliked_tasks=[
            "repetitive manual testing",
            "writing long documentation",
            "on-call incident response",
        ],
        preferred_work_modes=[
            "building/implementing",
            "autonomy",
            "product thinking",
            "engineering",
        ],
        work_opinions=[
            "implementation",
            "engineering",
            "building usable products",
            "automation reduces toil",
        ],
    )
