# 中文示例简历 — 北邮本科生，目标方向为 AI Agent / LLM 应用工程
# 示例数据均为合成内容，仅用于演示。

## Contact
- **Name**: 张伟
- **Education**: 北京邮电大学，通信工程本科，预计 2027 年毕业
- **Target Role**: AI Agent 应用开发工程师 / LLM 应用工程师

## Education
- 北京邮电大学，信息与通信工程学院，通信工程本科在读（2023–2027）
- 相关课程：数据结构、计算机网络、Python 程序设计、机器学习基础、数据库系统

## Skills
- **编程语言**: Python（主要）、C（课程项目）、SQL（基础）、HTML/CSS（基础）
- **框架与工具**: Git、VS Code、Jupyter、Linux CLI 基础、Docker（学习中）
- **AI/ML**: 熟悉 LLM API（OpenAI-compatible）、Prompt Engineering 基础、RAG 概念、Streamlit
- **领域理解**: 通信网络基础、KPI 指标、告警与工单流程

## Projects

### TelecomOps Agent（通信网络智能运维 Agent）
- 构建了一个基于 Streamlit 的 Agent 工作流，用于通信网络告警诊断，输入包括结构化 KPI 数据、异常检测规则和本地知识库。
- 实现了多 Agent 流程：Monitor Agent → Knowledge Agent → Diagnosis Agent → Ticket Agent。
- 使用确定性规则引擎，不强依赖 LLM，并保留证据追踪和假设记录。
- Technologies: Python, Streamlit, pandas, scikit-learn, agent orchestration patterns.
- Role: 独立开发。Repository: 本地项目。

### Course Project: Simple RAG Question-Answering System
- 构建了一个文档问答系统，采用类似 LangChain 的检索增强生成流程。
- 实现本地文档切分、sentence-transformers embedding 和 top-k 检索。
- 接入 OpenAI-compatible endpoint 进行答案生成，并保留引用链接。
- Technologies: Python, sentence-transformers, FAISS, Streamlit.
- Role: 独立开发。Repository: 课程项目，暂未公开。

### Campus Network Monitor Tool
- 编写 Python 脚本监控校园网络延迟和丢包情况，使用 ping/ICMP 获取结果。
- 将结果存储到 SQLite，并实现简单阈值告警。
- Technologies: Python, SQLite, subprocess.
- Role: 个人工具。

## Achievements
- 参加北邮校园 Hackathon（AI 方向，2025）
- 英语：CET-6 通过
- 通过在线课程和开源项目自学 LLM 应用开发

## Constraints
- 暂无正式行业实习经历
- 暂无已发表科研论文
- GitHub 账号较新，公开贡献仍有限
- 目标岗位：AI 应用工程方向，不投传统算法研究、教育培训、客服或销售岗位
