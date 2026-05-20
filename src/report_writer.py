"""Generate Markdown report from ResumeFitResult."""

from __future__ import annotations

from pathlib import Path
from src.schemas import ResumeFitResult
from src.localization import (
    category_label,
    dimension_label,
    display_text,
    honesty_label,
    priority_label,
    status_label,
)


def write_markdown_report(result: ResumeFitResult, output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = _render_report(result)
    out.write_text(md, encoding="utf-8")
    return out


def render_report_text(result: ResumeFitResult, language: str = "en") -> str:
    return _render_report(result, language=language)


def _render_report(result: ResumeFitResult, language: str = "en") -> str:
    r = result.fit_report
    resume = result.resume
    job = result.job
    lines: list[str] = []
    zh = language == "zh"

    lines.append("# ResumeFit Agent — 岗位匹配报告" if zh else "# ResumeFit Agent — Role Fit Report")
    lines.append("")
    lines.append(f"**{'候选人' if zh else 'Candidate'}:** {resume.name}")
    lines.append(f"**{'目标岗位' if zh else 'Target Role'}:** {display_text(resume.target_role, language)}")
    lines.append(f"**{'岗位名称' if zh else 'Job Title'}:** {display_text(job.title, language)}")
    lines.append(f"**{'级别信号' if zh else 'Seniority'}:** {display_text(job.seniority_signal, language)}")
    lines.append(f"**{'生成时间' if zh else 'Generated'}:** {_now()}")
    lines.append("")

    # ── Role Tendency ────────────────────────────────────────────────────
    if result.role_tendency is not None:
        rt = result.role_tendency
        lines.append("## 0. 岗位倾向预评估" if zh else "## 0. Pre-Fit Role Tendency Assessment")
        lines.append("")
        lines.append("> **Disclaimer:** " + rt.disclaimer)
        lines.append(">")
        lines.append("> **免责声明:** " + rt.disclaimer_zh)
        lines.append("")
        lines.append("### 推荐岗位方向排名" if zh else "### Ranked Role Directions")
        lines.append("")
        lines.append("| # | Role (EN) | Role (ZH) | Score |")
        lines.append("|---|---|---|---|")
        for i, role in enumerate(rt.ranked_roles, 1):
            lines.append(f"| {i} | {role.role_name_en} | {role.role_name_zh} | {role.score}/100 |")
        lines.append("")

        for i, role in enumerate(rt.ranked_roles, 1):
            lines.append(f"#### {i}. {role.role_name_en} ({role.role_name_zh}) — Score: {role.score}/100")
            lines.append("")
            lines.append(
                "> **注意：** 以下详细分析内容（匹配信号、注意事项、评分理由、下一步行动）"
                "目前为英文演示文本，尚未完成中文本地化。中文用户请参考上方角色名称与分数排名，"
                "详细解释请以英文内容为准。"
            )
            lines.append(">")
            lines.append(
                "> **Note:** The detailed analysis below (matched signals, cautions, "
                "scoring rationale, and next actions) is currently English demo text. "
                "Chinese localization for these sections is pending."
            )
            lines.append("")
            if role.matched_signals:
                lines.append("**匹配信号:**" if zh else "**Matched Signals / 匹配信号:**")
                for sig in role.matched_signals:
                    lines.append(f"- {display_text(sig, language)}")
                lines.append("")
            if role.caution_signals:
                lines.append("**注意事项:**" if zh else "**Cautions / 注意事项:**")
                for c in role.caution_signals:
                    lines.append(f"- {display_text(c, language)}")
                lines.append("")
            if role.rationale:
                lines.append("**评分理由:**" if zh else "**Scoring Rationale / 评分理由:**")
                for r_line in role.rationale:
                    lines.append(f"- {display_text(r_line, language)}")
                lines.append("")
            if role.next_proof_actions:
                lines.append("**下一步证明行动:**" if zh else "**Next Proof-Building Actions / 下一步证明行动:**")
                for a in role.next_proof_actions:
                    lines.append(f"- {display_text(a, language)}")
                lines.append("")
        lines.append("---")
        lines.append("")

    # ── Overall Score ───────────────────────────────────────────────────
    lines.append("## 1. 岗位匹配分数" if zh else "## 1. Role Match Score")
    lines.append("")
    lines.append(f"**{'综合分数' if zh else 'Overall Score'}:** {r.overall_score}/100 — *{display_text(r.score_label, language)}*")
    lines.append("")
    lines.append("### 维度分数" if zh else "### Dimension Scores")
    lines.append("")
    lines.append("| 维度 | 权重 | 分数 |" if zh else "| Dimension | Weight | Score |")
    lines.append("|---|---|---|")
    for dim, score in r.dimension_scores.items():
        label = dimension_label(dim, language)
        weight = _dim_weight(dim)
        lines.append(f"| {label} | {weight}% | {score} |")
    lines.append("")

    # ── Evidence Map ────────────────────────────────────────────────────
    lines.append("## 2. JD-证据地图" if zh else "## 2. JD-to-Evidence Map")
    lines.append("")
    status_icon = {"matched": "[MATCH]", "partial": "[PARTIAL]", "gap": "[GAP]"}
    for m in r.requirement_matches:
        icon = status_icon.get(m.status, "[?]")
        lines.append(f"### {icon} {display_text(m.requirement, language)}")
        lines.append(f"- **{'状态' if zh else 'Status'}:** {status_label(m.status, language)}")
        if m.evidence:
            for ev in m.evidence:
                lines.append(f"- **{'证据' if zh else 'Evidence'}:** {display_text(ev, language)}")
        if m.assumption:
            lines.append(f"- **{'说明' if zh else 'Note'}:** {display_text('Assumption-based assessment', language)}")
        if m.warning:
            lines.append(f"- **{'警告' if zh else 'Warning'}:** {display_text(m.warning, language)}")
        lines.append("")

    # ── Rewrite Suggestions ─────────────────────────────────────────────
    lines.append("## 3. 简历项目改写建议" if zh else "## 3. Resume Project Rewrite Suggestions")
    lines.append("")
    for i, s in enumerate(result.rewrite_suggestions, 1):
        lines.append(f"### {'建议' if zh else 'Suggestion'} {i}: {s.source_project}")
        lines.append(f"**{'目标 JD 要求' if zh else 'Targets JD requirement'}:** {display_text(s.target_jd_requirement, language)}")
        lines.append("")
        lines.append(f"**{'改写前' if zh else 'Before'}:**")
        lines.append(f"> {display_text(s.before_text, language)}")
        lines.append("")
        lines.append(f"**{'改写后' if zh else 'After'}:**")
        lines.append(f"> {display_text(s.after_text, language)}")
        lines.append("")
        lines.append(f"**{'证据' if zh else 'Evidence'}:** {display_text(s.evidence, language)}")
        lines.append(f"**{'真实性检查' if zh else 'Honesty check'}:** {honesty_label(s.honesty_note, language)}")
        lines.append("")

    # ── Skill Gaps ──────────────────────────────────────────────────────
    lines.append("## 4. 能力差距与证明计划" if zh else "## 4. Skill Gaps and Proof Plan")
    lines.append("")
    if result.skill_gaps:
        lines.append("| 能力 | 优先级 | 当前状态 | 目标状态 | 证明计划 |" if zh else "| Skill | Priority | Current State | Target | Proof Plan |")
        lines.append("|---|---|---|---|---|")
        for g in result.skill_gaps:
            lines.append(f"| {display_text(g.skill, language)} | {priority_label(g.priority, language)} | {display_text(g.current_state, language)} | {display_text(g.target_state, language)} | {display_text(g.proof_plan, language)} |")
    else:
        lines.append("*未识别出显著能力差距。*" if zh else "*No significant skill gaps identified.*")
    lines.append("")

    # ── Interview Questions ─────────────────────────────────────────────
    lines.append("## 5. 面试追问准备" if zh else "## 5. Interview Follow-Up Questions")
    lines.append("")
    for i, q in enumerate(result.interview_questions, 1):
        lines.append(f"### Q{i}: {display_text(q.question, language)}")
        lines.append(f"- **{'类别' if zh else 'Category'}:** {category_label(q.category, language)}")
        lines.append(f"- **{'针对点' if zh else 'Targets'}:** {display_text(q.target_weakness, language)}")
        if q.suggested_angle:
            lines.append(f"- **{'回答角度' if zh else 'Suggested angle'}:** {display_text(q.suggested_angle, language)}")
        lines.append("")

    # ── Portfolio Copy ──────────────────────────────────────────────────
    lines.append("## 6. 作品集展示文案" if zh else "## 6. Portfolio Display Copy")
    lines.append("")
    pc = result.portfolio_copy
    lines.append("### 短卡片" if zh else "### Short Card")
    lines.append("```")
    lines.append(display_text(pc.short_card, language))
    lines.append("```")
    lines.append("")
    lines.append("### README 标语" if zh else "### README Tagline")
    lines.append(f"> {display_text(pc.readme_tagline, language)}")
    lines.append("")
    lines.append("### 简历要点" if zh else "### Resume Bullets")
    for b in pc.resume_bullets:
        lines.append(f"- {display_text(b, language)}")
    lines.append("")
    lines.append("### 项目故事" if zh else "### Project Story")
    lines.append(display_text(pc.project_story, language))
    lines.append("")

    # ── Workflow Trace ──────────────────────────────────────────────────
    lines.append("## 7. 工作流追踪" if zh else "## 7. Workflow Trace")
    lines.append("")
    for step in result.workflow_trace:
        lines.append(f"### {step.agent}")
        lines.append(f"- **{'目标' if zh else 'Goal'}:** {display_text(step.goal, language)}")
        lines.append(f"- **{'输入' if zh else 'Inputs'}:** {', '.join(step.inputs) if step.inputs else 'N/A'}")
        lines.append(f"- **{'约束' if zh else 'Constraints'}:** {display_text(', '.join(step.constraints), language) if step.constraints else 'N/A'}")
        lines.append(f"- **{'证据' if zh else 'Evidence'}:** {display_text(', '.join(step.evidence), language) if step.evidence else 'N/A'}")
        lines.append(f"- **{'输出' if zh else 'Output'}:** {display_text(step.output, language)}")
        if step.assumptions:
            lines.append(f"- **{'假设' if zh else 'Assumptions'}:** {display_text(', '.join(step.assumptions), language)}")
        if step.verification:
            lines.append(f"- **{'验证' if zh else 'Verification'}:** {display_text(step.verification, language)}")
        lines.append("")

    # ── Verifier Report ─────────────────────────────────────────────────
    lines.append("## 8. 证据验证" if zh else "## 8. Evidence Verification")
    lines.append("")
    vr = result.verifier_report
    lines.append(f"- **{'总声明数' if zh else 'Total claims'}:** {vr.total_claims}")
    lines.append(f"- **{'有证据支撑' if zh else 'Evidence-backed'}:** {vr.evidence_backed}")
    lines.append(f"- **{'已标记假设' if zh else 'Assumption-flagged'}:** {vr.assumption_flagged}")
    lines.append(f"- **{'较弱或不可验证' if zh else 'Weak/unverifiable'}:** {vr.weak_or_unverifiable}")
    lines.append(f"- **{'是否通过' if zh else 'Passed'}:** {'是' if (zh and vr.passed) else '否' if zh else 'Yes' if vr.passed else 'No'}")
    if vr.violations:
        lines.append("")
        lines.append("### 违规项" if zh else "### Violations")
        for v in vr.violations:
            lines.append(f"- {display_text(v, language)}")
    lines.append("")

    # ── Risks ───────────────────────────────────────────────────────────
    lines.append("## 9. 风险与约束" if zh else "## 9. Risks and Constraints")
    lines.append("")
    if result.fit_report.risks:
        for risk in result.fit_report.risks:
            lines.append(f"- {display_text(risk, language)}")
    if result.constraints:
        lines.append("")
        lines.append("### 已声明约束" if zh else "### Declared Constraints")
        for c in result.constraints:
            lines.append(f"- {display_text(c, language)}")
    lines.append("")

    # ── Footer ──────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    if zh:
        lines.append("*本报告由 ResumeFit Agent 生成。*")
        lines.append("*示例数据仅用于演示；所有建议均要求有证据支撑，或显式标记为假设。*")
    else:
        lines.append("*Report generated by ResumeFit Agent — deterministic core workflow prototype.*")
        lines.append("*Sample data used. All recommendations are evidence-grounded or explicitly assumption-flagged.*")
        lines.append("*No real resume data, credentials, or paid APIs were used in this generation.*")
    lines.append("")

    return "\n".join(lines)


def _dim_weight(dim: str) -> int:
    weights = {
        "role_alignment": 25,
        "core_skill_match": 25,
        "project_evidence": 25,
        "github_proof": 15,
        "risk_honesty": 10,
    }
    return weights.get(dim, 0)


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
