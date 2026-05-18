# TelecomOps Agent — Reference Project Summary

> **NOTE**: This is a read-only reference summary. Do NOT modify the TelecomOps Agent repository.
> This document is for ResumeFit Agent evidence extraction only.

## Project Overview
- **Name**: TelecomOps Agent (通信网络智能运维 Agent 平台)
- **Type**: AI Agent application for telecom network operations
- **Role**: Reference project for AI Agent / AIOps / LLM Application engineering positioning

## Architecture
- Multi-agent workflow: Monitor Agent → Knowledge Agent → Diagnosis Agent → Ticket Agent
- Streamlit-based UI for interactive alarm triage and diagnosis
- Deterministic rules engine with local knowledge base (no API dependency)
- Evidence tracing: every diagnosis includes KPI evidence, assumptions, and confidence

## Technology Stack
- Python 3.8+, Streamlit, pandas, numpy, scikit-learn, plotly
- Agent orchestration: custom workflow engine with step-by-step evidence trace
- Data: synthetic KPI, alarm, and ticket data for demo

## Key Signals for ResumeFit
- Demonstrates agent architecture design (multi-agent pipeline with clear contracts)
- Evidence-grounded output (every workflow step records inputs, evidence, output, verification)
- Portfolio-ready: Streamlit UI, structured README (EN + zh-CN), smoke test, project documentation
- Domain-specific AI application (telecom) rather than generic LLM wrapper
- Deterministic fallback with assumption logging — shows engineering rigor

## Repository Structure
```
repo/
  app.py              # Streamlit entry point
  requirements.txt    # Python dependencies
  README.md           # EN documentation
  README.zh-CN.md     # Chinese documentation
  src/
    schemas.py        # Data classes
    agent_workflow.py # Workflow orchestration
    anomaly_detection.py
    data_loader.py
    diagnosis_engine.py
    retriever.py
    report_generator.py
    ticket_generator.py
    visualization.py
  data/
    alarms.csv, kpi.csv, tickets.csv
  scripts/
    smoke_test.py
  tests/
    ...
```

## What ResumeFit Agent Can Learn from This Project
- **Project packaging**: clean README with architecture diagram, setup instructions, and evidence examples
- **Agent workflow design**: named agents with clear input/output contracts
- **Evidence tracing**: WorkflowStep records goal, inputs, evidence, output, verification per step
- **Synthetic data**: safe, shareable demo data that demonstrates the system without real credentials
- **UI as thin layer**: business logic in src/, UI in app.py — separation of concerns
