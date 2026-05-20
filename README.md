# ResumeFit Agent

**AI Agent-powered resume-job fit analysis for AI engineering roles.**

ResumeFit Agent reads a resume, a target job description, and GitHub repository signals, then produces a structured role-fit report with evidence mapping, rewrite suggestions, skill gap analysis, interview prep questions, and portfolio copy. The Streamlit UI supports resume upload from Markdown, Word .docx, and best-effort legacy .doc files, then exports rewritten resume drafts as Markdown, Word .doc, and Word .docx.

## Live Demo

- Streamlit app: https://multica-agent-workflow-template-5xmbi6a5exwxxqorrhrnzn.streamlit.app/
- Chinese README: [README.zh-CN.md](README.zh-CN.md)

## Quick Start

```bash
pip install -r requirements.txt
python -B scripts/smoke_test.py
```

Run the Streamlit UI:

```bash
streamlit run app.py
```

Run tests:

```bash
python -m pytest
```

## Project Structure

```
repo/
  app.py              # Streamlit UI (optional)
  README.md
  requirements.txt
  data/
    sample_resume.md          # Synthetic sample resume
    sample_jd.md              # Synthetic sample JD
    github_profile.json        # Sample GitHub metadata
    repositories/              # Repository reference docs
  reports/                    # Generated reports
  scripts/
    smoke_test.py             # E2E smoke test
  src/
    schemas.py                # Data contracts (dataclasses)
    resume_parser.py          # Resume markdown parser
    jd_analyzer.py            # JD markdown parser
    github_evidence.py        # Repository evidence extractor
    fit_scoring.py            # Deterministic scoring rubric
    rewrite_coach.py          # Resume rewrite suggestions
    interview_prep.py         # Interview question generator
    portfolio_copy.py         # Portfolio text generator
    report_writer.py          # Markdown report generator
    agent_workflow.py         # Workflow orchestrator
    verifier.py               # Evidence verification
    sample_data.py            # Sample data loader
  tests/
    test_fit_scoring.py
    test_agent_workflow.py
```

## Agent Workflow

1. **Resume Parser** — extracts candidate facts, projects, skills, constraints
2. **JD Analyzer** — extracts requirements, skills, hidden signals from JD
3. **GitHub Evidence Agent** — maps repository metadata to project evidence
4. **Fit Scoring Agent** — applies 5-dimension weighted rubric (role alignment 25%, skill match 25%, project evidence 25%, GitHub proof 15%, risk/honesty 10%)
5. **Rewrite Coach Agent** — generates before/after project bullet rewrites
6. **Skill Gap Agent** — identifies gaps with priority, proof plan, resources
7. **Interview Prep Agent** — generates follow-up questions and answer angles
8. **Portfolio Copy Agent** — generates homepage/README-ready copy
9. **Verifier** — checks evidence grounding on every claim

## Scoring Rubric

| Score | Label |
|---|---|
| 80-100 | Strong match with clear evidence |
| 60-79 | Plausible match with targeted rewrite and proof gaps |
| 40-59 | Partial match; needs focused artifact building |
| <40 | Not recommended without major repositioning |

## Constraints

- **Deterministic only** — no LLM API calls required
- **No network** — runs entirely offline with sample data
- **No secrets** — no API keys, tokens, or credentials needed
- **Evidence-grounded** — every recommendation has evidence or is assumption-flagged
- **No fabrication** — never generates fake metrics, experience, or credentials
- **Sample data** — all inputs are synthetic, labeled, and safe to share
- **Resume file support** — Markdown and .docx are preferred; legacy .doc parsing is best-effort and should be reviewed before use

## Tech Stack

Python 3.8+, dataclasses, Streamlit (optional UI), python-docx, olefile

## Deployment

This project is ready for Streamlit Community Cloud:

- Main file: `app.py`
- Python dependencies: `requirements.txt`
- Runtime behavior: offline deterministic demo with synthetic sample data
- Secrets required: none

## License

This is a portfolio project. All sample data is synthetic.
