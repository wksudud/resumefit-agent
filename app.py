"""ResumeFit Agent — Streamlit UI prototype."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from src.schemas import ResumeFitInputs
from src.agent_workflow import run_resume_fit_workflow
from src.report_writer import render_report_text
from src.resume_io import (
    build_rewritten_resume_doc,
    build_rewritten_resume_docx,
    build_rewritten_resume_markdown,
    read_uploaded_resume,
)
from src.sample_data import load_resume_text, load_jd_text, load_github_profile, load_repo_docs, load_sample_questionnaire
from src.role_tendency import score_role_tendency, build_sample_questionnaire
from src.localization import (
    category_label,
    dimension_label,
    display_text,
    honesty_label,
    priority_label,
    status_label,
)


TEXT = {
    "en": {
        "language_label": "Language",
        "language_name": "English",
        "title": "ResumeFit Agent",
        "caption": "AI Agent-powered resume-job fit analysis | Offline rules + optional API mode",
        "mode_label": "Generation mode",
        "mode_offline": "Offline rules (no API)",
        "mode_api": "API enhanced",
        "api_key": "API key",
        "api_base_url": "API base URL",
        "api_model": "API model",
        "api_help": "Uses an OpenAI-compatible /chat/completions endpoint. The key is only used for this session.",
        "api_missing": "API mode needs an API key. Without it, the app falls back to offline results.",
        "mode_status": "Mode",
        "tabs": [
            "Input", "Role Tendency", "Match Overview",
            "Evidence Map", "Rewrites & Gaps",
            "Interview Prep", "Export",
        ],
        "input_workspace": "Input Workspace",
        "role_tendency_title": "Pre-Fit Role Tendency Assessment",
        "role_tendency_desc": "Help discover which AI roles best fit your personality, interests, and work style — no target role needed.",
        "role_tendency_disclaimer": "Heuristic career guidance based on self-reported signals. Not a psychological diagnosis.",
        "personality": "Personality / Work Style",
        "courses": "Courses Learned / Enjoyed",
        "interests": "Interests",
        "dislikes": "Disliked Tasks",
        "work_modes": "Preferred Work Modes",
        "work_opinions": "Opinions About Work",
        "run_tendency": "Assess Role Tendency",
        "assessing": "Analyzing role tendencies...",
        "tendency_complete": "Role tendency assessment complete!",
        "ranked_roles": "Ranked Role Directions",
        "role_score": "Score",
        "matched_signals": "Matched Signals",
        "cautions": "Cautions",
        "next_actions": "Next Proof-Building Actions",
        "no_tendency": "Run the role tendency assessment first (this tab).",
        "role_detail_locale_note": "Role names, project names, and technology names may remain bilingual.",
        "scoring_rationale": "Scoring Rationale / 评分理由",
        "use_sample_questionnaire": "Use sample questionnaire",
        "use_sample": "Use sample data",
        "upload_resume": "Upload resume",
        "upload_help": "Supports Markdown, Word .docx, and best-effort legacy .doc parsing.",
        "upload_success": "Loaded resume from uploaded file.",
        "legacy_doc_best_effort_warning": "Loaded a legacy .doc file with best-effort text extraction. Please review the text before analysis.",
        "legacy_doc_empty_warning": "Could not extract readable text from this legacy .doc file. Please convert it to .docx or .md, then upload it again.",
        "unsupported_upload_warning": "Unsupported resume file type. Please upload .md, .markdown, .docx, or .doc.",
        "resume": "Resume",
        "jd": "Job Description (Markdown)",
        "run": "Run Analysis",
        "running": "Running ResumeFit Agent workflow...",
        "complete": "Analysis complete!",
        "match_overview": "Match Overview",
        "run_first": "Run the analysis first (Input tab).",
        "sample_locale_note": "Sample resume and JD follow the selected language.",
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
        "export_rewritten": "Export Rewritten Resume Draft",
        "download_resume_md": "Download Rewritten Resume (Markdown)",
        "download_resume_doc": "Download Rewritten Resume (Word .doc)",
        "download_resume_docx": "Download Rewritten Resume (Word .docx)",
        "constraints": ["Sample data only", "Deterministic generation"],
    },
    "zh": {
        "language_label": "语言",
        "language_name": "中文",
        "title": "ResumeFit Agent",
        "caption": "面向求职场景的简历-岗位匹配 Agent | 离线规则 + 可选 API 增强",
        "mode_label": "生成模式",
        "mode_offline": "离线规则（不使用 API）",
        "mode_api": "API 增强",
        "api_key": "API Key",
        "api_base_url": "API Base URL",
        "api_model": "API 模型",
        "api_help": "使用 OpenAI-compatible /chat/completions 接口。Key 只在本次页面会话中使用。",
        "api_missing": "API 增强模式需要 API key。未填写时会自动回退到离线结果。",
        "mode_status": "模式",
        "tabs": [
            "输入", "角色倾向", "匹配概览",
            "证据地图", "改写与差距",
            "面试准备", "导出",
        ],
        "input_workspace": "输入工作区",
        "role_tendency_title": "岗位角色倾向预评估",
        "role_tendency_desc": "帮助你发现自己最适合的 AI 岗位方向 — 无需提前选定目标岗位。",
        "role_tendency_disclaimer": "基于自述信号的启发式职业引导，非心理诊断。",
        "personality": "性格 / 工作风格",
        "courses": "学习或喜欢的课程",
        "interests": "兴趣方向",
        "dislikes": "不喜欢的任务",
        "work_modes": "偏好的工作模式",
        "work_opinions": "对工作的看法",
        "run_tendency": "评估岗位倾向",
        "assessing": "正在分析岗位倾向...",
        "tendency_complete": "岗位倾向评估完成！",
        "ranked_roles": "推荐岗位方向排名",
        "role_score": "分数",
        "matched_signals": "匹配信号",
        "cautions": "注意信号",
        "next_actions": "下一步证明行动",
        "no_tendency": "请先运行岗位倾向评估（本页）。",
        "role_detail_locale_note": "岗位名、项目名和技术名会保留必要的中英混排。",
        "scoring_rationale": "评分理由 / Scoring Rationale",
        "use_sample_questionnaire": "使用示例问卷",
        "use_sample": "使用示例数据",
        "upload_resume": "上传简历",
        "upload_help": "支持 Markdown、Word .docx，并对旧版 .doc 进行尽力文本解析。",
        "upload_success": "已从上传文件读取简历。",
        "legacy_doc_best_effort_warning": "已用尽力模式读取旧版 .doc 文件。分析前请先检查文本是否完整。",
        "legacy_doc_empty_warning": "无法从该旧版 .doc 文件中提取可读文本。请先转换为 .docx 或 .md 后重新上传。",
        "unsupported_upload_warning": "不支持的简历文件类型。请上传 .md、.markdown、.docx 或 .doc。",
        "resume": "简历",
        "jd": "岗位描述（Markdown）",
        "run": "开始分析",
        "running": "正在运行 ResumeFit Agent 工作流...",
        "complete": "分析完成！",
        "match_overview": "匹配概览",
        "run_first": "请先在“输入”页运行分析。",
        "sample_locale_note": "示例简历和岗位描述会跟随当前语言切换。",
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
        "export_rewritten": "导出改写后简历草稿",
        "download_resume_md": "下载改写后简历（Markdown）",
        "download_resume_doc": "下载改写后简历（Word .doc）",
        "download_resume_docx": "下载改写后简历（Word .docx）",
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

mode_options = ["offline", "api"]
generation_mode = st.sidebar.radio(
    t["mode_label"],
    options=mode_options,
    format_func=lambda code: t["mode_offline"] if code == "offline" else t["mode_api"],
)
api_key = ""
api_base_url = "https://api.openai.com/v1"
api_model = "gpt-4o-mini"
if generation_mode == "api":
    st.sidebar.caption(t["api_help"])
    api_base_url = st.sidebar.text_input(t["api_base_url"], value=api_base_url)
    api_model = st.sidebar.text_input(t["api_model"], value=api_model)
    api_key = st.sidebar.text_input(t["api_key"], type="password")
    if not api_key:
        st.sidebar.warning(t["api_missing"])

st.title(t["title"])
st.caption(t["caption"])
st.caption(f"{t['mode_status']}: {t['mode_offline'] if generation_mode == 'offline' else t['mode_api']}")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(t["tabs"])

# Initialize session state
if "result" not in st.session_state:
    st.session_state.result = None
if "last_resume_text" not in st.session_state:
    st.session_state.last_resume_text = ""
if "role_tendency_input" not in st.session_state:
    st.session_state.role_tendency_input = None
if "role_tendency_result" not in st.session_state:
    st.session_state.role_tendency_result = None

REPO_DIR = os.path.dirname(os.path.abspath(__file__))


def sample_file_path(stem: str, lang: str) -> str:
    if lang == "zh":
        zh_path = os.path.join(REPO_DIR, "data", f"{stem}.zh-CN.md")
        if os.path.exists(zh_path):
            return zh_path
    return os.path.join(REPO_DIR, "data", f"{stem}.md")

with tab1:
    st.header(t["input_workspace"])
    st.caption(t["sample_locale_note"])

    col1, col2 = st.columns(2)
    with col1:
        use_sample = st.checkbox(t["use_sample"], value=True)
        uploaded_resume = st.file_uploader(
            t["upload_resume"],
            type=["md", "markdown", "docx", "doc"],
            help=t["upload_help"],
        )
        uploaded_resume_text = ""
        if uploaded_resume is not None:
            uploaded_resume_text, upload_warning = read_uploaded_resume(uploaded_resume)
            if upload_warning == "legacy_doc_best_effort":
                st.warning(t["legacy_doc_best_effort_warning"])
            elif upload_warning == "legacy_doc_empty":
                st.warning(t["legacy_doc_empty_warning"])
            elif upload_warning:
                st.warning(t["unsupported_upload_warning"])
            elif uploaded_resume_text:
                st.success(t["upload_success"])

        default_resume_text = load_resume_text(sample_file_path("sample_resume", language)) if use_sample else ""
        if uploaded_resume_text:
            default_resume_text = uploaded_resume_text

        resume_text = st.text_area(
            t["resume"],
            value=default_resume_text,
            height=250,
        )
    with col2:
        jd_text = st.text_area(
            t["jd"],
            value=load_jd_text(sample_file_path("sample_jd", language)) if use_sample else "",
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
                role_tendency_input=st.session_state.get("role_tendency_input"),
                generation_mode=generation_mode,
                api_key=api_key,
                api_base_url=api_base_url,
                api_model=api_model,
            )
            st.session_state.result = run_resume_fit_workflow(inputs)
            st.session_state.last_resume_text = resume_text
        st.success(t["complete"])

with tab2:
    st.header(t["role_tendency_title"])
    st.caption(t["role_tendency_desc"])
    st.info(t["role_tendency_disclaimer"])

    use_sample_q = st.checkbox(t["use_sample_questionnaire"], value=True)

    if "role_tendency_input" not in st.session_state:
        st.session_state.role_tendency_input = None
    if "role_tendency_result" not in st.session_state:
        st.session_state.role_tendency_result = None

    if use_sample_q:
        default_q = build_sample_questionnaire()
    else:
        default_q = None

    col_a, col_b = st.columns(2)
    with col_a:
        personality = st.text_area(
            t["personality"],
            value=", ".join(default_q.personality_style) if default_q else "",
            height=100,
            placeholder="e.g. builder, systems thinker, autonomous, curious...",
            key="personality_field",
        )
        courses = st.text_area(
            t["courses"],
            value=", ".join(default_q.courses_learned) if default_q else "",
            height=100,
            placeholder="e.g. prompt engineering, langchain, python, docker...",
            key="courses_field",
        )
        interests = st.text_area(
            t["interests"],
            value=", ".join(default_q.interests) if default_q else "",
            height=100,
            placeholder="e.g. autonomous systems, agent architecture, automation...",
            key="interests_field",
        )
    with col_b:
        dislikes = st.text_area(
            t["dislikes"],
            value=", ".join(default_q.disliked_tasks) if default_q else "",
            height=100,
            placeholder="e.g. repetitive manual testing, on-call response...",
            key="dislikes_field",
        )
        work_modes = st.text_area(
            t["work_modes"],
            value=", ".join(default_q.preferred_work_modes) if default_q else "",
            height=100,
            placeholder="e.g. building/implementing, autonomy, product thinking...",
            key="modes_field",
        )
        opinions = st.text_area(
            t["work_opinions"],
            value=", ".join(default_q.work_opinions) if default_q else "",
            height=100,
            placeholder="e.g. implementation, engineering, automation reduces toil...",
            key="opinions_field",
        )

    if st.button(t["run_tendency"], type="primary", key="run_tendency_btn"):
        with st.spinner(t["assessing"]):
            from src.schemas import RoleTendencyInput
            tendency_input = RoleTendencyInput(
                personality_style=[s.strip() for s in personality.split(",") if s.strip()],
                courses_learned=[s.strip() for s in courses.split(",") if s.strip()],
                interests=[s.strip() for s in interests.split(",") if s.strip()],
                disliked_tasks=[s.strip() for s in dislikes.split(",") if s.strip()],
                preferred_work_modes=[s.strip() for s in work_modes.split(",") if s.strip()],
                work_opinions=[s.strip() for s in opinions.split(",") if s.strip()],
            )
            tendency_result = score_role_tendency(tendency_input)
            st.session_state.role_tendency_input = tendency_input
            st.session_state.role_tendency_result = tendency_result
        st.success(t["tendency_complete"])

    if st.session_state.role_tendency_result is not None:
        rt = st.session_state.role_tendency_result
        st.subheader(t["ranked_roles"])

        for i, role in enumerate(rt.ranked_roles, 1):
            score_color = (
                "green" if role.score >= 60 else
                "orange" if role.score >= 35 else "red"
            )
            with st.expander(
                f"#{i} {role.role_name_en} / {role.role_name_zh} — "
                f":{score_color}[{role.score}/100]"
            ):
                st.caption(t["role_detail_locale_note"])
                if role.matched_signals:
                    st.write(f"**{t['matched_signals']}:**")
                    for sig in role.matched_signals:
                        st.write(f"- {display_text(sig, language)}")
                if role.caution_signals:
                    st.write(f"**{t['cautions']}:**")
                    for c in role.caution_signals:
                        st.warning(display_text(c, language))
                if role.rationale:
                    st.write(f"**{t['scoring_rationale']}:**")
                    for r_line in role.rationale:
                        st.write(f"- {display_text(r_line, language)}")
                if role.next_proof_actions:
                    st.write(f"**{t['next_actions']}:**")
                    for a in role.next_proof_actions:
                        st.info(display_text(a, language))
    else:
        st.info(t["no_tendency"])

with tab3:
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
            label = dimension_label(dim, language)
            st.progress(score / 100, text=f"{label}: {score}%")

        st.caption(display_text(r.score_label, language))

with tab4:
    st.header(t["evidence_map"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for m in st.session_state.result.fit_report.requirement_matches:
            icon = {"matched": "", "partial": "", "gap": ""}.get(m.status, "")
            with st.expander(f"{icon} {display_text(m.requirement, language)} ({status_label(m.status, language)})"):
                if m.evidence:
                    for ev in m.evidence:
                        st.write(f"- {display_text(ev, language)}")
                if m.assumption:
                    st.warning(t["assumption"])
                if m.warning:
                    st.warning(display_text(m.warning, language))

with tab5:
    st.header(t["rewrites"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for s in st.session_state.result.rewrite_suggestions:
            target_label = display_text(s.target_jd_requirement, language)
            with st.expander(f"{s.source_project} -> {target_label[:60]}..."):
                st.write(f"**{t['before']}:**")
                st.info(display_text(s.before_text, language))
                st.write(f"**{t['after']}:**")
                st.success(display_text(s.after_text, language))
                st.caption(f"{t['evidence']}: {display_text(s.evidence, language)}")
                st.caption(f"{t['honesty']}: {honesty_label(s.honesty_note, language)}")

    st.header(t["skill_gaps"])
    if st.session_state.result and st.session_state.result.skill_gaps:
        for g in st.session_state.result.skill_gaps:
            with st.expander(f"{display_text(g.skill, language)} ({priority_label(g.priority, language)} {t['priority']})"):
                st.write(f"**{t['current']}:** {display_text(g.current_state, language)}")
                st.write(f"**{t['target']}:** {display_text(g.target_state, language)}")
                st.write(f"**{t['proof_plan']}:** {display_text(g.proof_plan, language)}")
                st.write(f"**{t['resource']}:** {display_text(g.suggested_resource, language)}")

with tab6:
    st.header(t["interview"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        for i, q in enumerate(st.session_state.result.interview_questions, 1):
            question_text = display_text(q.question, language)
            with st.expander(f"Q{i}: {question_text[:80]}..."):
                st.write(f"**{t['category']}:** {category_label(q.category, language)}")
                st.write(f"**{t['angle']}:** {display_text(q.suggested_angle, language)}")

with tab7:
    st.header(t["export"])
    if st.session_state.result is None:
        st.info(t["run_first"])
    else:
        result = st.session_state.result
        pc = result.portfolio_copy
        st.subheader(t["short_card"])
        st.code(display_text(pc.short_card, language))
        st.subheader(t["tagline"])
        st.info(display_text(pc.readme_tagline, language))
        st.subheader(t["bullets"])
        for b in pc.resume_bullets:
            st.write(f"- {display_text(b, language)}")
        st.subheader(t["story"])
        st.write(display_text(pc.project_story, language))

        st.divider()
        st.subheader(t["export_md"])
        report_md = render_report_text(result, language=language)
        st.download_button(
            t["download"],
            report_md,
            file_name="resumefit_report.md",
            mime="text/markdown",
        )

        st.divider()
        st.subheader(t["export_rewritten"])
        rewritten_md = build_rewritten_resume_markdown(
            st.session_state.last_resume_text,
            result.rewrite_suggestions,
            language=language,
        )
        rewritten_docx = build_rewritten_resume_docx(rewritten_md)
        rewritten_doc = build_rewritten_resume_doc(rewritten_md)
        st.download_button(
            t["download_resume_md"],
            rewritten_md,
            file_name="rewritten_resume.md",
            mime="text/markdown",
        )
        st.download_button(
            t["download_resume_doc"],
            rewritten_doc,
            file_name="rewritten_resume.doc",
            mime="application/msword",
        )
        st.download_button(
            t["download_resume_docx"],
            rewritten_docx,
            file_name="rewritten_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
