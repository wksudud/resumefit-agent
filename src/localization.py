"""Display localization helpers for generated ResumeFit artifacts."""

from __future__ import annotations

import re


STATUS_LABELS = {
    "zh": {
        "matched": "匹配",
        "partial": "部分匹配",
        "gap": "差距",
    }
}

PRIORITY_LABELS = {
    "zh": {
        "high": "高",
        "medium": "中",
        "low": "低",
    }
}

DIMENSION_LABELS = {
    "zh": {
        "role_alignment": "岗位方向匹配",
        "core_skill_match": "核心技能匹配",
        "project_evidence": "项目证据",
        "github_proof": "GitHub 证明",
        "risk_honesty": "风险与诚实度",
    }
}

CATEGORY_LABELS = {
    "zh": {
        "skill-gap": "能力差距",
        "project-detail": "项目细节",
        "scenario": "情景题",
        "project-deep-dive": "项目深挖",
        "architecture": "架构理解",
    }
}

HONESTY_LABELS = {
    "zh": {
        "evidence-backed": "有证据支撑",
        "assumption-based": "基于假设",
    }
}

SCORE_LABELS_ZH = {
    "strong match with clear evidence": "证据清晰，匹配度强",
    "plausible match with targeted rewrite and proof gaps": "具备匹配潜力，需要定向改写和补充证明",
    "partial match; needs focused artifact building": "部分匹配，需要集中补充作品证明",
    "not recommended without major repositioning": "除非大幅重新定位，否则不建议投递",
}

TEXT_REPLACEMENTS_ZH = [
    ("Assumption-based assessment", "基于假设的评估"),
    ("Assumption-based match - needs verification with real project evidence", "基于假设的匹配，需要真实项目证据进一步验证"),
    ("Keyword match:", "关键词匹配："),
    ("Partial keyword match:", "部分关键词匹配："),
    ("No matching signal", "未发现匹配信号"),
    ("found in resume or project evidence", "出现在简历或项目证据中"),
    ("found", "已找到"),
    ("Project README", "项目 README"),
    ("Based on project", "基于项目"),
    ("description and technology stack", "描述与技术栈"),
    ("evidence-backed", "有证据支撑"),
    ("assumption-based", "基于假设"),
    ("LLM Output Evaluation", "LLM 输出评估"),
    ("Automated Testing", "自动化测试"),
    ("CI/CD Pipelines", "CI/CD 流水线"),
    ("API Design (FastAPI/REST)", "API 设计（FastAPI/REST）"),
    ("No formal evaluation framework demonstrated", "尚未展示正式的评估框架"),
    ("Build an eval harness measuring accuracy, faithfulness, relevance", "建立评估工具，衡量准确性、忠实度和相关性"),
    ("Create a benchmark script for project outputs with pass/fail criteria and metrics", "为项目输出创建带通过标准和指标的基准测试脚本"),
    ("Limited test infrastructure in projects", "项目测试基础设施仍有限"),
    ("Add pytest coverage for core workflow and scoring logic", "为核心工作流和评分逻辑添加 pytest 覆盖"),
    ("Write unit tests for fit_scoring.py and integration test for agent_workflow.py", "为 fit_scoring.py 编写单元测试，并为 agent_workflow.py 编写集成测试"),
    ("No CI/CD demonstrated", "尚未展示 CI/CD 能力"),
    ("Add GitHub Actions workflow for lint, test, smoke", "添加 GitHub Actions 工作流执行 lint、测试和 smoke 检查"),
    ("Create .github/workflows/ci.yml with pytest and smoke test steps", "创建 .github/workflows/ci.yml，包含 pytest 和 smoke test 步骤"),
    ("No API design experience demonstrated", "尚未展示 API 设计经验"),
    ("Add FastAPI wrapper around core workflow for headless access", "为核心工作流添加 FastAPI 封装，支持无界面调用"),
    ("Create api.py with /analyze endpoint wrapping run_resume_fit_workflow", "创建 api.py，用 /analyze 端点封装 run_resume_fit_workflow"),
    ("Provide a concrete before/after or problem/solution story. Include measurable outcome if available, or state scope clearly.", "给出具体的改写前后或问题-解决方案故事；如果有可量化结果就说明，没有则清楚界定范围。"),
    ("Show system design thinking, trade-off reasoning, and honest reflection on limitations", "展示系统设计思路、取舍理由，以及对局限性的诚实反思。"),
    ("Demonstrate ability to abstract patterns and make intentional design choices", "展示你能抽象架构模式，并有意识地做设计选择。"),
    ("Your resume shows some experience with", "你的简历显示你具备一些关于"),
    ("This role requires", "该岗位要求"),
    ("Can you describe any experience you have with this, even from coursework or self-study?", "你是否有相关经验？课程项目、自学或个人项目都可以。"),
    ("Can you give a specific example of how you applied it in a project?", "的经验。能否举一个你在项目中应用它的具体例子？"),
    ("Walk me through the architecture of", "请讲解"),
    ("What were the key design decisions and what would you do differently?", "的架构。关键设计决策是什么？如果重做你会如何改进？"),
    ("How would you compare your two main projects in terms of agent architecture decisions? What pattern did each use and why?", "如果从 Agent 架构决策角度比较你的两个主要项目，它们分别用了什么模式？为什么？"),
    ("Designed and implemented", "设计并实现"),
    ("Built an interactive", "构建了交互式"),
    ("dashboard using Streamlit", "Streamlit 仪表盘"),
    ("Authored comprehensive documentation for", "为"),
    ("including architecture diagrams, setup guide, API contracts, and evidence-trace examples in the project README.", "编写了完整文档，包括架构图、安装指南、API 契约和 README 中的证据追踪示例。"),
    ("Applied software engineering best practices to", "在"),
    ("structured project layout, clean module interfaces (via dataclasses), deterministic testing without external API dependencies, and evidence-traced output generation.", "中应用软件工程实践：结构化项目布局、基于 dataclass 的清晰模块接口、不依赖外部 API 的确定性测试，以及带证据追踪的输出生成。"),
    ("Built with", "技术栈包括"),
    ("BUPT CS undergraduate building AI Agent applications and LLM-powered workflows.", "北邮本科生，关注 AI Agent 应用与 LLM 工作流工程。"),
    ("Portfolio signal:", "作品集信号："),
    ("against target JD.", "相对于目标 JD。"),
    ("An AI Agent workflow that demonstrates multi-agent orchestration, evidence-grounded output, and disciplined software engineering", "一个展示多 Agent 编排、证据驱动输出和工程化实践的 AI Agent 工作流"),
    ("built as a portfolio project for", "作为面向"),
    ("roles.", "岗位的作品集项目。"),
    ("I built", "我构建"),
    ("to demonstrate practical AI Agent engineering skills beyond simple API wrappers.", "是为了展示超越简单 API 封装的 AI Agent 工程能力。"),
    ("The system uses a deterministic multi-agent workflow with defined contracts between agents, step-level evidence tracing, and a scoring rubric that makes quality measurable.", "系统采用确定性的多 Agent 工作流，定义 Agent 间契约，记录步骤级证据，并用评分规则让质量可衡量。"),
    ("Every output is traceable to input evidence or flagged as an explicit assumption.", "每个输出都能追溯到输入证据，或被明确标记为假设。"),
    ("This project reflects my approach: product-aware engineering, honest about limitations, and focused on building trustworthy AI systems.", "这个项目体现了我的方法：有产品意识的工程实现、诚实面对局限，并专注构建可信的 AI 系统。"),
]


def display_text(value: object, language: str = "en") -> str:
    text = "" if value is None else str(value)
    if language != "zh":
        return text
    text = SCORE_LABELS_ZH.get(text, text)
    for source, target in TEXT_REPLACEMENTS_ZH:
        text = text.replace(source, target)
    text = (
        text.replace("。.", "。")
        .replace("？.", "？")
        .replace("，.", "，")
        .replace(" .", "。")
    )
    text = re.sub(r"(?<=[\u4e00-\u9fff）】])\.\s*", "。", text)
    text = re.sub(
        r"你的简历显示你具备一些关于\s*(.+?)。\s*的经验。能否举一个你在项目中应用它的具体例子？",
        r"你的简历显示你具备一些“\1”相关经验。能否举一个你在项目中应用它的具体例子？",
        text,
    )
    text = re.sub(
        r"请讲解\s*(.+?)。的架构。",
        r"请讲解“\1”的架构。",
        text,
    )
    return text


def status_label(status: str, language: str = "en") -> str:
    if language == "zh":
        return STATUS_LABELS["zh"].get(status, status)
    return status


def priority_label(priority: str, language: str = "en") -> str:
    if language == "zh":
        return PRIORITY_LABELS["zh"].get(priority, priority)
    return priority


def dimension_label(dimension: str, language: str = "en") -> str:
    if language == "zh":
        return DIMENSION_LABELS["zh"].get(dimension, dimension)
    return dimension.replace("_", " ").title()


def category_label(category: str, language: str = "en") -> str:
    if language == "zh":
        return CATEGORY_LABELS["zh"].get(category, category)
    return category


def honesty_label(honesty: str, language: str = "en") -> str:
    if language == "zh":
        return HONESTY_LABELS["zh"].get(honesty, display_text(honesty, language))
    return honesty
