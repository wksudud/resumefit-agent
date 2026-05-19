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


TEXT = {
    "en": {
        "language_label": "Language",
        "language_name": "English",
        "title": "ResumeFit Agent",
        "caption": "AI Agent-powered resume-job fit analysis | Deterministic prototype",
        "tabs": [
            "Input", "Match Overview", "Evidence Map",
            "Rewrites & Gaps", "Interview Prep", "Export",
        ],
        "input_workspace": "Input Workspace",
        "use_sample": "Use sample data",
        "resume": "Resume (Markdown)",
        "jd": "Job Description (Markdown)",
        "run": "Run Analysis",
        "running": "Running ResumeFit Agent workflow...",
        "complete": "Analysis complete!",
        "match_overview": "Match Overview",
        "run_first": "Run the analysis first (Input tab).",
        "overall_score": "Overall Score",
        "matched": "Matched",
        "partial": "Partial",
        "gaps": "Gaps",
        "dimension_scores": "Dimension Scores",
        "evidence_map": "Evidence Map",
        "assumption": "Assumption-based assessment",
        "rewrites": "Resume Rewrite Suggestions",
        "before": "Before",
        "after": "After",
        "evidence": "Evidence",
        "honesty": "Honesty",
        "skill_gaps": "Skill Gaps",
        "priority": "priority",
        "current": "Current",
        "target": "Target",
        "proof_plan": "Proof plan",
        "resource": "Resource",
        "interview": "Interview Follow-Up Questions",
        "category": "Category",
        "angle": "Suggested angle",
        "export": "Portfolio Copy & Export",
        "short_card": "Short Card",
        "tagline": "README Tagline",
        "bullets": "Resume Bullets",
        "story": "Project Story",
        "export_md": "Export Markdown Report",
        "download": "Download Report (Markdown)",
        "constraints": ["Sample data only", "Deterministic generation"],
    },
    "zh": {
        "language_label": "语言",
        "language_name": "中文",
        "title": "ResumeFit Agent",
        "caption": "面向求职场景的简历-岗位匹配 Agent | 离线确定性原型",
        "tabs": [
            "输入", "匹配概览", "证据地图",
            "改写与差距", "面试准备", "导出",
        ],
        "input_workspace": "输入工作区",
        "use_sample": "使用示例数据",
        "resume": "简历（Markdown）",
        "jd": "岗位描述（Markdown）",
        "run": "开始分析",
        "running": "正在运行 ResumeFit Agent 工作流...",
        "complete": "分析完成！",
        "match_overview": "匹配概览",
        "run_first": "请先在“输入”页运行分析。",
        "overall_score": "综合分数",
        "matched": "匹配",
        "partial": "部分匹配",
        "gaps": "差距",
        "dimension_scores": "维度得分",
        "evidence_map": "证据地图",
        "assumption": "基于假设的评估",
        "rewrites": "简历改写建议",
        "before": "改写前",
        "after": "改写后",
        "evidence": "证据",
        "honesty": "真实性",
        "skill_gaps": "能力差距",
        "priority": "优先级",
        "current": "当前状态",
        "target": "目标状态",
        "proof_plan": "证明计划",
        "resource": "建议资源",
        "interview": "面试追问准备",
        "category": "类别",
        "angle": "回答角度",
        "export": "作品集文案与导出",
        "short_card": "短卡片",
        "tagline": "README 标语",
        "bullets": "简历要点",
        "story": "项目故事",
        "export_md": "导出 Markdown 报告",
        "download": "下载报告（Markdown）",
        "constraints": ["仅使用示例数据", "确定性生成"],
    },
}

st.set_page_config(
    page_title="ResumeFit Agent",
    page_icon="",
    layout="wide",
)

language = st.sidebar.radio(
    TEXT["en"]["language_label"],
    options=["en", "zh"],
    format_func=lambda code: TEXT[code]["language_name"],
    horizontal=True,
)
t = TEXT[language]

st.title(t["title"])
st.caption(t["caption"])

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(t["tabs"])

# Initialize session state
if "result" not in st.session_state:
    st.session_state.result = None

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

with tab1:
    st.header(t["input_workspace"])

    col1, col2 = st.columns(2)
    with col1:
        use_sample = st.checkbox(t["use_sample"], value=True)
        resume_text = st.text_area(
            t["resume"],
            value=load_resume_text() if use_sample else "",
            height=250,
        )
    with col2:
        jd_text = st.text_area(
            t["jd"],
            value=load_jd_text() if use_sample else "",
            height=250,
        )

    if st.button(t["run"], type="primary"):
        with st.spinner(t["running"]):
            profile_path = os.path.join(REPO_DIR, "data", "github_profile.json")
            repo_docs_dir = os.path.join(REPO_DIR, "data", "repositories")

            inputs = ResumeFitInputs(
                resume_text=resume_text,
                jd_text=jd_text,
                github_profile_path=profile_path,
                repo_docs_dir=repo_docs_dir,
                output_report_path=os.path.join(REPO_DIR, "reports", "fit_report.md"),
                constraints=t["constraints"],
            )
            st.session_state.result = run_resume_fit_workflow(inputs)
        st.success(t["complete"])

with tab2:
    st.header(t["match_overview"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        r = st.session_state.result.fit_report
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t["overall_score"], f"{r.overall_score}/100")
        col2.metric(t["matched"], r.matched_count)
        col3.metric(t["partial"], r.partial_count)
        col4.metric(t["gaps"], r.gap_count)

        st.subheader(t["dimension_scores"])
        for dim, score in r.dimension_scores.items():
            label = dim.replace("_", " ").title()
            st.progress(score / 100, text=f"{label}: {score}%")

        st.caption(r.score_label)

with tab3:
    st.header(t["evidence_map"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for m in st.session_state.result.fit_report.requirement_matches:
            icon = {"matched": "", "partial": "", "gap": ""}.get(m.status, "")
            with st.expander(f"{icon} {m.requirement} ({m.status})"):
                if m.evidence:
                    for ev in m.evidence:
                        st.write(f"- {ev}")
                if m.assumption:
                    st.warning(t["assumption"])
                if m.warning:
                    st.warning(m.warning)

with tab4:
    st.header(t["rewrites"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for s in st.session_state.result.rewrite_suggestions:
            with st.expander(f"{s.source_project} -> {s.target_jd_requirement[:60]}..."):
                st.write(f"**{t['before']}:**")
                st.info(s.before_text)
                st.write(f"**{t['after']}:**")
                st.success(s.after_text)
                st.caption(f"{t['evidence']}: {s.evidence}")
                st.caption(f"{t['honesty']}: {s.honesty_note}")

    st.header(t["skill_gaps"])
    if st.session_state.result and st.session_state.result.skill_gaps:
        for g in st.session_state.result.skill_gaps:
            with st.expander(f"{g.skill} ({g.priority} {t['priority']})"):
                st.write(f"**{t['current']}:** {g.current_state}")
                st.write(f"**{t['target']}:** {g.target_state}")
                st.write(f"**{t['proof_plan']}:** {g.proof_plan}")
                st.write(f"**{t['resource']}:** {g.suggested_resource}")

with tab5:
    st.header(t["interview"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for i, q in enumerate(st.session_state.result.interview_questions, 1):
            with st.expander(f"Q{i}: {q.question[:80]}..."):
                st.write(f"**{t['category']}:** {q.category}")
                st.write(f"**{t['angle']}:** {q.suggested_angle}")

with tab6:
    st.header(t["export"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        result = st.session_state.result
        pc = result.portfolio_copy
        st.subheader(t["short_card"])
        st.code(pc.short_card)
        st.subheader(t["tagline"])
        st.info(pc.readme_tagline)
        st.subheader(t["bullets"])
        for b in pc.resume_bullets:
            st.write(f"- {b}")
        st.subheader(t["story"])
        st.write(pc.project_story)

        st.divider()
        st.subheader(t["export_md"])
        report_md = render_report_text(result)
        st.download_button(
            t["download"],
            report_md,
            file_name="resumefit_report.md",
            mime="text/markdown",
        )
