"""ResumeFit Agent — Streamlit UI prototype."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from src.schemas import ResumeFitInputs
from src.agent_workflow import run_resume_fit_workflow
from src.report_writer import render_report_text
from src.sample_data import load_resume_text, load_jd_text, load_github_profile, load_repo_docs

st.set_page_config(
    page_title="ResumeFit Agent",
    page_icon="",
    layout="wide",
)

st.title("ResumeFit Agent")
st.caption("AI Agent-powered resume-job fit analysis | Deterministic prototype")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Input", "Match Overview", "Evidence Map",
    "Rewrites & Gaps", "Interview Prep", "Export",
])

# Initialize session state
if "result" not in st.session_state:
    st.session_state.result = None

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

with tab1:
    st.header("Input Workspace")

    col1, col2 = st.columns(2)
    with col1:
        use_sample = st.checkbox("Use sample data", value=True)
        resume_text = st.text_area(
            "Resume (Markdown)",
            value=load_resume_text() if use_sample else "",
            height=250,
        )
    with col2:
        jd_text = st.text_area(
            "Job Description (Markdown)",
            value=load_jd_text() if use_sample else "",
            height=250,
        )

    if st.button("Run Analysis", type="primary"):
        with st.spinner("Running ResumeFit Agent workflow..."):
            profile_path = os.path.join(REPO_DIR, "data", "github_profile.json")
            repo_docs_dir = os.path.join(REPO_DIR, "data", "repositories")

            inputs = ResumeFitInputs(
                resume_text=resume_text,
                jd_text=jd_text,
                github_profile_path=profile_path,
                repo_docs_dir=repo_docs_dir,
                output_report_path=os.path.join(REPO_DIR, "reports", "fit_report.md"),
                constraints=["Sample data only", "Deterministic generation"],
            )
            st.session_state.result = run_resume_fit_workflow(inputs)
        st.success("Analysis complete!")

with tab2:
    st.header("Match Overview")
    if st.session_state.result is None:
        st.info("Run the analysis first (Input tab).")
    else:
        r = st.session_state.result.fit_report
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Score", f"{r.overall_score}/100")
        col2.metric("Matched", r.matched_count)
        col3.metric("Partial", r.partial_count)
        col4.metric("Gaps", r.gap_count)

        st.subheader("Dimension Scores")
        for dim, score in r.dimension_scores.items():
            label = dim.replace("_", " ").title()
            st.progress(score / 100, text=f"{label}: {score}%")

        st.caption(r.score_label)

with tab3:
    st.header("Evidence Map")
    if st.session_state.result is None:
        st.info("Run the analysis first (Input tab).")
    else:
        for m in st.session_state.result.fit_report.requirement_matches:
            icon = {"matched": "", "partial": "", "gap": ""}.get(m.status, "")
            with st.expander(f"{icon} {m.requirement} ({m.status})"):
                if m.evidence:
                    for ev in m.evidence:
                        st.write(f"- {ev}")
                if m.assumption:
                    st.warning("Assumption-based assessment")
                if m.warning:
                    st.warning(m.warning)

with tab4:
    st.header("Resume Rewrite Suggestions")
    if st.session_state.result is None:
        st.info("Run the analysis first (Input tab).")
    else:
        for s in st.session_state.result.rewrite_suggestions:
            with st.expander(f"{s.source_project} -> {s.target_jd_requirement[:60]}..."):
                st.write("**Before:**")
                st.info(s.before_text)
                st.write("**After:**")
                st.success(s.after_text)
                st.caption(f"Evidence: {s.evidence}")
                st.caption(f"Honesty: {s.honesty_note}")

    st.header("Skill Gaps")
    if st.session_state.result and st.session_state.result.skill_gaps:
        for g in st.session_state.result.skill_gaps:
            with st.expander(f"{g.skill} ({g.priority} priority)"):
                st.write(f"**Current:** {g.current_state}")
                st.write(f"**Target:** {g.target_state}")
                st.write(f"**Proof plan:** {g.proof_plan}")
                st.write(f"**Resource:** {g.suggested_resource}")

with tab5:
    st.header("Interview Follow-Up Questions")
    if st.session_state.result is None:
        st.info("Run the analysis first (Input tab).")
    else:
        for i, q in enumerate(st.session_state.result.interview_questions, 1):
            with st.expander(f"Q{i}: {q.question[:80]}..."):
                st.write(f"**Category:** {q.category}")
                st.write(f"**Suggested angle:** {q.suggested_angle}")

with tab6:
    st.header("Portfolio Copy & Export")
    if st.session_state.result is None:
        st.info("Run the analysis first (Input tab).")
    else:
        result = st.session_state.result
        pc = result.portfolio_copy
        st.subheader("Short Card")
        st.code(pc.short_card)
        st.subheader("README Tagline")
        st.info(pc.readme_tagline)
        st.subheader("Resume Bullets")
        for b in pc.resume_bullets:
            st.write(f"- {b}")
        st.subheader("Project Story")
        st.write(pc.project_story)

        st.divider()
        st.subheader("Export Markdown Report")
        report_md = render_report_text(result)
        st.download_button(
            "Download Report (Markdown)",
            report_md,
            file_name="resumefit_report.md",
            mime="text/markdown",
        )
