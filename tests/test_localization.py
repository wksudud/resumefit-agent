from pathlib import Path

from src.agent_workflow import run_resume_fit_workflow
from src.localization import category_label, display_text, status_label
from src.report_writer import render_report_text
from src.sample_data import load_jd_text, load_resume_text
from src.schemas import ResumeFitInputs


def test_loads_chinese_sample_data():
    resume = load_resume_text(language="zh")
    jd = load_jd_text(language="zh")

    assert "中文示例简历" in resume
    assert "中文示例岗位描述" in jd
    assert "## Contact" in resume
    assert "## Required Skills" in jd


def test_display_text_localizes_common_interview_question():
    text = (
        "Your resume shows some experience with 至少完成过一个 AI 应用项目。 "
        "Can you give a specific example of how you applied it in a project?"
    )

    localized = display_text(text, "zh")

    assert "相关经验" in localized
    assert "specific example" not in localized


def test_chinese_report_uses_localized_sections():
    base = Path(__file__).resolve().parent.parent
    inputs = ResumeFitInputs(
        resume_text=load_resume_text(language="zh"),
        jd_text=load_jd_text(language="zh"),
        github_profile_path=str(base / "data" / "github_profile.json"),
        repo_docs_dir=str(base / "data" / "repositories"),
    )

    result = run_resume_fit_workflow(inputs)
    report = render_report_text(result, language="zh")

    assert "岗位匹配报告" in report
    assert "JD-证据地图" in report
    assert "面试追问准备" in report
    assert "证据验证" in report


def test_localized_labels():
    assert status_label("partial", "zh") == "部分匹配"
    assert category_label("project-detail", "zh") == "项目细节"
