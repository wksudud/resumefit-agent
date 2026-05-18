# ResumeFit Agent

A deterministic Agent workflow for resume-job fit analysis and career intelligence.

## Overview
ResumeFit Agent reads resume text, job descriptions, and GitHub repository evidence, then runs a multi-agent pipeline to produce: role-fit scoring, evidence mapping, resume rewrite suggestions, skill gap analysis, interview preparation questions, and portfolio copy. Designed as a demonstration of AI Agent product engineering with ethical constraints.

## Technology Stack
- Python 3.11+
- Pydantic / dataclasses (Data contracts)
- Streamlit (UI prototype)
- Template-based deterministic generation (LLM adapter optional)

## Architecture
- **Resume Parser Agent:** Extracts candidate facts, projects, skills from markdown/resume text
- **JD Analyzer Agent:** Parses job requirements into structured categories with importance signals
- **GitHub Evidence Agent:** Maps repository metadata to concrete project evidence signals
- **Fit Scoring Agent:** Applies a weighted rubric (role alignment, skill match, project evidence, GitHub proof, honesty constraints)
- **Rewrite Coach Agent:** Produces before/after project bullet rewrites with evidence annotation
- **Interview Prep Agent:** Generates likely follow-up questions from gaps and weak signals
- **Portfolio Copy Agent:** Generates homepage and README-ready copy
- **Verifier:** Checks that every recommendation has evidence or an explicit assumption flag

## Key Signals (Agent/LLM/AIOps)
- 8-agent deterministic workflow with defined interface contracts
- Scoring rubric with transparent dimension weights
- Evidence-trace for every recommendation
- Honesty check: no fabricated metrics or experience
- Portfolio-ready output suitable for personal homepage

## Repository Structure
```
resumefit-agent/
  app.py
  src/
    agent_workflow.py
    schemas.py
    resume_parser.py
    jd_analyzer.py
    github_evidence.py
    fit_scoring.py
    rewrite_coach.py
    interview_prep.py
    portfolio_copy.py
    report_writer.py
    verifier.py
    sample_data.py
  data/
    sample_resume.md
    sample_jd.md
    github_profile.json
    repositories/
  scripts/
    smoke_test.py
  reports/
```

## Evidence Quality
- All modules are deterministic and testable without API keys or network
- Interface contracts defined via dataclasses
- Smoke test covers the full workflow end-to-end
- README documents architecture, constraints, and ethical guidelines
