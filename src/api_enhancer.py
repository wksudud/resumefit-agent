"""Optional OpenAI-compatible API enhancement for ResumeFit outputs."""

from __future__ import annotations

import json
from urllib import error, request

from src.schemas import (
    InterviewQuestion,
    PortfolioCopy,
    ResumeFitResult,
    RewriteSuggestion,
    WorkflowStep,
)


def enhance_with_api(result: ResumeFitResult, api_key: str, base_url: str, model: str) -> ResumeFitResult:
    """Enhance deterministic artifacts with an LLM API while preserving evidence.

    The deterministic workflow remains the source of truth. The API is only asked
    to improve wording and interview angles from already-generated evidence.
    """
    if not api_key.strip():
        result.errors.append("API mode selected, but no API key was provided. Used offline results only.")
        result.generation_mode = "offline"
        return result

    provider = _provider_label(base_url, model)
    payload = {
        "resume": result.resume.to_dict(),
        "job": result.job.to_dict(),
        "fit_report": result.fit_report.to_dict(),
        "rewrite_suggestions": [s.to_dict() for s in result.rewrite_suggestions[:8]],
        "interview_questions": [q.to_dict() for q in result.interview_questions[:6]],
        "portfolio_copy": result.portfolio_copy.to_dict(),
    }

    prompt = (
        "Improve the following resume-fit artifacts for a junior AI/agent engineering candidate. "
        "Return strict JSON with keys rewrite_suggestions, interview_questions, portfolio_copy. "
        "Do not invent companies, metrics, credentials, internships, publications, or project outcomes. "
        "Preserve evidence and honesty_note fields. Keep every claim grounded in the input. "
        "If evidence is weak, use conservative wording.\n\n"
        f"INPUT_JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        content = _chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative resume writing assistant. "
                        "You improve wording but never fabricate facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        data = _parse_json_content(content)
        _apply_rewrites(result, data.get("rewrite_suggestions", []))
        _apply_interview_questions(result, data.get("interview_questions", []))
        _apply_portfolio_copy(result, data.get("portfolio_copy", {}))

        result.generation_mode = "api"
        result.api_provider = provider
        result.workflow_trace.append(WorkflowStep(
            agent="API Enhancement Agent",
            goal="Use an OpenAI-compatible chat completion API to polish wording without changing facts",
            inputs=["deterministic ResumeFitResult", "API model"],
            constraints=[
                "API key is never stored in repository files",
                "No fabricated achievements, metrics, credentials, or employers",
                "Deterministic scoring and evidence mapping remain source of truth",
            ],
            evidence=[f"Provider/model: {provider}", "Structured JSON response parsed"],
            output="Enhanced rewrite suggestions, interview angles, and portfolio copy",
            assumptions=["LLM output is treated as wording assistance, not verified fact"],
            verification="Verifier still runs after API enhancement",
        ))
    except Exception as exc:
        result.errors.append(f"API enhancement failed: {exc}. Used offline results only.")
        result.generation_mode = "offline"

    return result


def _chat_completion(api_key: str, base_url: str, model: str, messages: list[dict[str, str]]) -> str:
    endpoint = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model.strip() or "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    req = request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=45) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:300]}") from exc

    data = json.loads(raw)
    return data["choices"][0]["message"]["content"]


def _parse_json_content(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()
    return json.loads(content)


def _apply_rewrites(result: ResumeFitResult, items: list[dict]) -> None:
    if not items:
        return
    updated: list[RewriteSuggestion] = []
    for original, item in zip(result.rewrite_suggestions, items):
        updated.append(RewriteSuggestion(
            source_project=item.get("source_project") or original.source_project,
            target_jd_requirement=item.get("target_jd_requirement") or original.target_jd_requirement,
            before_text=item.get("before_text") or original.before_text,
            after_text=item.get("after_text") or original.after_text,
            evidence=item.get("evidence") or original.evidence,
            honesty_note=item.get("honesty_note") or original.honesty_note,
        ))
    updated.extend(result.rewrite_suggestions[len(updated):])
    result.rewrite_suggestions = updated


def _apply_interview_questions(result: ResumeFitResult, items: list[dict]) -> None:
    if not items:
        return
    updated: list[InterviewQuestion] = []
    for original, item in zip(result.interview_questions, items):
        updated.append(InterviewQuestion(
            question=item.get("question") or original.question,
            category=item.get("category") or original.category,
            target_weakness=item.get("target_weakness") or original.target_weakness,
            suggested_angle=item.get("suggested_angle") or original.suggested_angle,
        ))
    updated.extend(result.interview_questions[len(updated):])
    result.interview_questions = updated


def _apply_portfolio_copy(result: ResumeFitResult, item: dict) -> None:
    if not item:
        return
    original = result.portfolio_copy
    result.portfolio_copy = PortfolioCopy(
        short_card=item.get("short_card") or original.short_card,
        readme_tagline=item.get("readme_tagline") or original.readme_tagline,
        resume_bullets=item.get("resume_bullets") or original.resume_bullets,
        project_story=item.get("project_story") or original.project_story,
    )


def _provider_label(base_url: str, model: str) -> str:
    clean_url = base_url.rstrip("/") or "OpenAI-compatible API"
    clean_model = model.strip() or "default model"
    return f"{clean_model} via {clean_url}"
