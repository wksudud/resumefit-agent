"""Extract project evidence from GitHub profile JSON and repository docs."""

from __future__ import annotations

import json
from pathlib import Path

from src.schemas import ProjectEvidence

# Keywords that signal Agent / LLM / AIOps work
AGENT_KW = [
    "agent", "multi-agent", "workflow", "orchestrat", "pipeline",
    "tool use", "tool calling", "function call", "planning",
]
LLM_KW = [
    "llm", "large language model", "gpt", "openai", "prompt",
    "rag", "retrieval", "embedding", "vector", "generation",
    "langchain", "llamaindex", "anthropic",
]
AIOPS_KW = [
    "aiops", "operations", "monitoring", "alert", "incident",
    "diagnosis", "ticket", "automation", "infrastructure",
    "telecom", "network", "kpi", "alarm", "runbook",
]


def extract_github_evidence(
    github_profile: dict,
    repo_docs: dict[str, str],
) -> list[ProjectEvidence]:
    evidence_items: list[ProjectEvidence] = []

    repos = github_profile.get("repositories", [])
    if not repos and "profile" in github_profile:
        # The data may be a wrapper with a 'repositories' key at top level,
        # or nested under 'profile'
        pass

    for repo in repos:
        name = repo.get("name", "unknown")
        doc_text = repo_docs.get(name, repo_docs.get(name.replace("-", "_"), ""))

        agent_signals = _scan_signals(repo, doc_text, AGENT_KW)
        llm_signals = _scan_signals(repo, doc_text, LLM_KW)
        aiops_signals = _scan_signals(repo, doc_text, AIOPS_KW)
        all_signals = agent_signals + llm_signals + aiops_signals

        measurable = _extract_measurable(repo, doc_text)
        warnings = _identify_weak_evidence(repo, doc_text)

        evidence_items.append(ProjectEvidence(
            project_name=name,
            source=repo.get("description", ""),
            technologies=_extract_tech(repo, doc_text),
            agent_llm_aiops_signals=all_signals,
            measurable_proof=measurable,
            weak_evidence_warnings=warnings,
            read_only=True,
        ))

    return evidence_items


def _scan_signals(repo: dict, doc_text: str, keywords: list[str]) -> list[str]:
    haystack = (
        doc_text.lower() + " " +
        " ".join(repo.get("topics", [])).lower() + " " +
        repo.get("description", "").lower()
    )
    found: list[str] = []
    for kw in keywords:
        if kw.lower() in haystack:
            # Use the doc text to provide a brief context snippet
            found.append(f"Signal '{kw}' detected in project {repo.get('name', '')}")
    return found


def _extract_tech(repo: dict, doc_text: str) -> list[str]:
    tech: list[str] = []
    lang = repo.get("language", "")
    if lang:
        tech.append(lang)
    topics = repo.get("topics", [])
    tech.extend(topics)
    # Also scan doc text for technology mentions
    for line in doc_text.split("\n"):
        s = line.strip()
        if s.lower().startswith("technologies:") or s.lower().startswith("tech stack:"):
            if ":" in s:
                tech_str = s.split(":", 1)[1]
                tech.extend(t.strip() for t in tech_str.replace("、", ",").split(",") if t.strip())
    return list(dict.fromkeys(tech))  # deduplicate preserving order


def _extract_measurable(repo: dict, doc_text: str) -> list[str]:
    proofs: list[str] = []

    commit_count = repo.get("commit_count", 0)
    if commit_count >= 15:
        proofs.append(f"{commit_count} commits: sustained development effort")
    elif commit_count >= 8:
        proofs.append(f"{commit_count} commits: moderate development activity")
    elif commit_count > 0:
        proofs.append(f"{commit_count} commits: limited but real development activity")

    if repo.get("has_readme"):
        proofs.append("Has README: project documentation exists")
    else:
        proofs.append("No README: documentation gap (assumed based on repo metadata)")

    if repo.get("has_tests"):
        proofs.append("Has tests: test infrastructure present")
    else:
        proofs.append("No tests detected: test coverage unverified (assumption)")

    if repo.get("is_public"):
        proofs.append("Public repository: visible to employers")
    else:
        proofs.append("Private/local repository: not visible to employers without access")

    return proofs


def _identify_weak_evidence(repo: dict, doc_text: str) -> list[str]:
    warnings: list[str] = []
    if not repo.get("has_readme"):
        warnings.append(f"Project '{repo.get('name', '')}' lacks README — documentation is weak")
    if not repo.get("has_tests"):
        warnings.append(f"Project '{repo.get('name', '')}' has no tests — code quality unverified")
    if repo.get("stars", 0) == 0 and repo.get("forks", 0) == 0:
        warnings.append(f"Project '{repo.get('name', '')}' has no community engagement signals")
    if repo.get("commit_count", 0) < 5:
        warnings.append(f"Project '{repo.get('name', '')}' has very few commits — limited scope")
    if not repo.get("is_public", True):
        warnings.append(f"Project '{repo.get('name', '')}' is not public — unverifiable by employer")
    return warnings
