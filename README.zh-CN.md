# ResumeFit Agent 中文说明

ResumeFit Agent 是一个面向 AI 工程岗位求职场景的简历-岗位匹配工具。它读取简历、目标岗位 JD 和 GitHub 项目信号，输出结构化匹配报告，包括岗位适配分数、证据映射、简历改写建议、能力差距、面试追问和作品集展示文案。Streamlit 网页端支持上传 Markdown、Word .docx 和尽力解析的旧版 .doc 简历，并可导出改写后的 Markdown、Word .doc 和 Word .docx 草稿。

## 在线体验

- Streamlit 在线版：https://multica-agent-workflow-template-5xmbi6a5exwxxqorrhrnzn.streamlit.app/
- 英文 README：[README.md](README.md)

## 核心能力

1. 岗位倾向预评估：根据用户自述的性格、课程、兴趣、工作偏好和对工作的看法，给出适合的 AI 岗位方向。
2. 简历-JD 匹配分析：用确定性规则分析简历和岗位描述之间的匹配程度。
3. 证据地图：把岗位要求映射到简历、项目和 GitHub 证据。
4. 简历改写建议：基于已有证据生成更贴合岗位的项目表述，不编造经历和指标。
5. 能力差距和证明计划：指出需要补足的能力，并给出可展示的作品集行动建议。
6. 面试准备：生成可能被追问的问题和回答角度。
7. 导出报告：生成 Markdown 格式的岗位适配报告。
8. 简历文件导入/导出：支持 .md、.docx、旧版 .doc 尽力解析，并导出 .md、.doc、.docx 三种改写草稿。

## 快速运行

安装依赖：

```bash
pip install -r requirements.txt
```

运行本地 smoke test：

```bash
python -B scripts/smoke_test.py
```

启动 Streamlit UI：

```bash
streamlit run app.py
```

运行测试：

```bash
python -m pytest
```

如果本地没有安装 `pytest`，仍可以先运行 `scripts/smoke_test.py` 做最小可用性检查。

## 项目结构

```text
repo/
  app.py                    # Streamlit UI
  README.md                 # English README
  README.zh-CN.md           # 中文说明
  requirements.txt
  data/                     # 合成示例数据
  reports/                  # 生成的报告
  scripts/
    smoke_test.py           # 端到端 smoke test
  src/
    schemas.py              # 数据结构契约
    role_tendency.py        # 岗位倾向评估
    resume_parser.py        # 简历解析
    jd_analyzer.py          # JD 解析
    github_evidence.py      # GitHub 项目信号提取
    fit_scoring.py          # 匹配评分
    rewrite_coach.py        # 简历改写建议
    interview_prep.py       # 面试追问
    portfolio_copy.py       # 作品集展示文案
    report_writer.py        # Markdown 报告生成
    agent_workflow.py       # 工作流编排
    verifier.py             # 证据校验
  tests/
```

## 工作流

1. Role Tendency Agent：在 JD 匹配前进行岗位倾向预评估。
2. Resume Parser：抽取候选人的项目、技能、教育和约束条件。
3. JD Analyzer：抽取岗位要求、技能和隐藏信号。
4. GitHub Evidence Agent：从项目元数据和文档中提取证据。
5. Fit Scoring Agent：按 5 个维度生成匹配分数。
6. Rewrite Coach Agent：生成基于证据的简历改写建议。
7. Skill Gap Agent：输出能力差距和补证计划。
8. Interview Prep Agent：生成面试追问和回答方向。
9. Portfolio Copy Agent：生成作品集展示文案。
10. Verifier：检查输出是否有证据支撑，或是否明确标记为假设。

## 评分维度

| 维度 | 权重 |
|---|---:|
| 岗位方向匹配 | 25% |
| 核心技能匹配 | 25% |
| 项目证据 | 25% |
| GitHub 证明 | 15% |
| 风险和诚实度 | 10% |

## 安全边界

- 不调用 LLM API。
- 不需要 API key、token 或账号凭据。
- 不访问网络即可运行核心流程。
- 示例数据全部为合成数据。
- 不编造经历、指标、公司或真实项目成果。
- 所有建议必须有证据支撑，或显式标记为假设。
- Markdown 和 .docx 是推荐格式；旧版 .doc 属于尽力解析，使用前需要检查文本是否完整。

## 部署说明

该项目适合部署到 Streamlit Community Cloud：

- 入口文件：`app.py`
- 依赖文件：`requirements.txt`
- Secrets：不需要
- 默认数据：仓库内合成示例数据

## 许可证

这是一个作品集项目。仓库内示例数据均为合成数据。
