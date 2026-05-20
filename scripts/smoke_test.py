"""Smoke test for ResumeFit Agent core workflow.

Usage: python -B scripts/smoke_test.py
"""

import sys
import os

# Ensure the repo/ directory is on sys.path
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_DIR)

from src.schemas import ResumeFitInputs
from src.sample_data import load_resume_text, load_jd_text, load_github_profile, load_repo_docs
from src.agent_workflow import run_resume_fit_workflow
from src.report_writer import write_markdown_report, render_report_text
from src.verifier import verify_result


def main():
    print("=" * 60)
    print("ResumeFit Agent — Smoke Test")
    print("=" * 60)

    # 1. Load sample data
    print("\n[1/5] Loading sample data...")
    resume_text = load_resume_text()
    jd_text = load_jd_text()
    github_profile = load_github_profile()
    repo_docs = load_repo_docs()
    print(f"  Resume: {len(resume_text)} chars")
    print(f"  JD: {len(jd_text)} chars")
    print(f"  GitHub repos: {len(github_profile.get('repositories', []))}")
    print(f"  Repo docs: {len(repo_docs)} files")

    # 2. Run workflow
    print("\n[2/5] Running agent workflow...")
    # Need to pass profile as dict through inputs; workflow loads JSON from path
    import json
    profile_path = os.path.join(REPO_DIR, "data", "github_profile.json")
    repo_docs_dir = os.path.join(REPO_DIR, "data", "repositories")

    # Also pass the in-memory data via a temp approach
    # The workflow loads from paths; ensure paths are valid
    inputs = ResumeFitInputs(
        resume_text=resume_text,
        jd_text=jd_text,
        github_profile_path=profile_path,
        repo_docs_dir=repo_docs_dir,
        output_report_path=os.path.join(REPO_DIR, "reports", "fit_report.md"),
        constraints=[
            "Sample data only — not real candidate information",
            "Deterministic template generation — no LLM API calls",
            "GitHub metadata is synthetic for demo purposes",
        ],
    )

    result = run_resume_fit_workflow(inputs)
    print(f"  Overall score: {result.fit_report.overall_score}/100")
    print(f"  Score label: {result.fit_report.score_label}")
    print(f"  Matched: {result.fit_report.matched_count}")
    print(f"  Partial: {result.fit_report.partial_count}")
    print(f"  Gaps: {result.fit_report.gap_count}")
    print(f"  Rewrites: {len(result.rewrite_suggestions)}")
    print(f"  Interview questions: {len(result.interview_questions)}")
    print(f"  Workflow steps: {len(result.workflow_trace)}")
    print(f"  Errors: {len(getattr(result, 'errors', []))}")

    # 3. Run verifier
    print("\n[3/5] Verifying evidence grounding...")
    verifier_report = verify_result(result)
    print(f"  Total claims: {verifier_report.total_claims}")
    print(f"  Evidence-backed: {verifier_report.evidence_backed}")
    print(f"  Assumption-flagged: {verifier_report.assumption_flagged}")
    print(f"  Violations: {len(verifier_report.violations)}")
    print(f"  Passed: {verifier_report.passed}")

    if verifier_report.violations:
        print("  Violations:")
        for v in verifier_report.violations:
            print(f"    - {v}")

    # 4. Generate report
    print("\n[4/5] Generating Markdown report...")
    report_path = write_markdown_report(result, inputs.output_report_path)
    print(f"  Report written to: {report_path}")

    # Print the report to stdout as well
    print("\n" + "=" * 60)
    print(render_report_text(result))
    print("=" * 60)

    # 5. Acceptance checks
    print("\n[5/5] Acceptance checks...")
    checks = []

    # Check 1: Role match score present
    checks.append(("Role match score present", result.fit_report.overall_score > 0))

    # Check 2: Evidence map exists
    checks.append(("Evidence map (requirement matches)",
                   len(result.fit_report.requirement_matches) > 0))

    # Check 3: 3+ rewrite suggestions
    checks.append(("3+ rewrite suggestions",
                   len(result.rewrite_suggestions) >= 3))

    # Check 4: Skill gaps with priority
    has_prioritized_gaps = all(g.priority in ("high", "medium", "low")
                               for g in result.skill_gaps) if result.skill_gaps else False
    checks.append(("Skill gaps with priority", has_prioritized_gaps))

    # Check 5: Interview questions present
    checks.append(("Interview questions present",
                   len(result.interview_questions) > 0))

    # Check 6: Portfolio copy present
    checks.append(("Portfolio copy present",
                   result.portfolio_copy is not None
                   and len(result.portfolio_copy.resume_bullets) > 0))

    # Check 7: Workflow trace present
    checks.append(("Workflow trace with steps",
                   len(result.workflow_trace) >= 7))

    # Check 8: No fabricated metrics
    no_violations = len(verifier_report.violations) == 0
    checks.append(("No fabricated metrics (verifier passed)", no_violations))

    # Check 9: Recommendations have evidence or assumption
    checks.append(("Evidence or assumption on all claims",
                   verifier_report.evidence_backed + verifier_report.assumption_flagged
                   >= verifier_report.total_claims))

    # Check 10: TelecomOps reference present
    telecom_ref = any("telecomops" in s.source_project.lower()
                      or "telecomops" in s.evidence.lower()
                      for s in result.rewrite_suggestions)
    checks.append(("TelecomOps Agent referenced as evidence", telecom_ref))

    # --- Readback/structure checks on app.py (UI format strings) ---
    import re
    app_path = os.path.join(REPO_DIR, "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        app_source = f.read()

    # Check 11: expander label f-string has {role.score} properly braced
    # Pattern validates the source code contains :{score_color}[{role.score}/100] literally
    expander_label_ok = bool(re.search(
        r':\{score_color\}\[\{role\.score\}/100\]',
        app_source
    ))
    checks.append(("app.py expander uses {role.score} (not bare role.score})", expander_label_ok))

    # Check 12: no broken format patterns like "role.score}" without opening brace
    broken_brace = re.search(r'\[role\.score\}', app_source)
    checks.append(("app.py has no unbraced [role.score} patterns", broken_brace is None))

    all_passed = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] {label}")

    print("\n" + "=" * 60)
    if all_passed:
        print("SMOKE TEST PASSED")
    else:
        print("SMOKE TEST FAILED — see failures above")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
