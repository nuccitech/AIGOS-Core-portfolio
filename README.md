# AIGOS — Campaign Workflow (Portfolio Slice)

A focused, runnable slice of [AIGOS (Content Autopilot)](#about-aigos), the production multi-tenant SaaS I built solo. This repository extracts one production workflow — the campaign generation pipeline — and runs it end-to-end against a real (or mocked) LLM, with real validation, real policy evaluation, and real persistence.

This is **not** a stripped-down marketing tour. The pipeline you see here is the same shape and structure used in production, with proprietary prompts, tenant logic, and vendor integrations removed. Everything that *is* in this repo is real, non-trivial code.

---

## What's actually in here

| Stage | What it does | Implementation |
|---|---|---|
| `validate` | Parses + validates a campaign brief (audience, channels, constraints, must-include keywords) | Pydantic models with cross-field validation |
| `plan` | Allocates the brief across channels with channel-specific objectives and length budgets | Deterministic planner with per-channel rules |
| `draft` | Generates per-channel copy | Real OpenAI call with `OPENAI_API_KEY`; deterministic template fallback otherwise |
| `policy` | Evaluates drafts against a rule set: length, banned terms, required keywords, claim-flagging | Rule engine returning `approved` / `needs_review` / `rejected` with per-rule reasons |
| `insights` | Scores audience fit and channel priority, surfaces risk flags | Deterministic scoring; explainable outputs |
| `persist` | Writes the campaign + outputs to SQLite | SQLAlchemy 2.0, real schema |

Each stage is composable. The pipeline runner threads a `PipelineContext` through them in order, short-circuiting on hard rejects. See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the design rationale and tradeoffs.

---

## Quick demo

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

In another shell:

```bash
curl -X POST http://127.0.0.1:5000/api/workflows/campaign \
  -H "Content-Type: application/json" \
  -d @webapp/utils/mock_data.json
```

Without an OpenAI key, drafts come from the template fallback. Set one to get real model output:

```bash
export OPENAI_API_KEY=sk-...
python app.py
```

The response is the full pipeline trace, not a canned payload. Re-run with `webapp/utils/mock_data_bad.json` to see a policy rejection with structured reasons.

---

## Architecture in one paragraph

Stages are independent units that take a `PipelineContext` and return a `StageResult`. Routes stay thin (parse request → kick off pipeline → return result). Services hold business logic. Integrations are interfaces — the OpenAI provider is one of several swappable implementations in production. State flows explicitly through the context; nothing reaches into globals. The pipeline runner is ~40 lines and handles ordering, error envelope, and tracing. The detailed rationale (why stages over a single service method, why explicit context over DI per-stage, where this falls down) is in [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite covers the validator, the policy rule engine, each stage in isolation, and a full pipeline run against a fake LLM provider.

---

## Directory layout

```
webapp/
├── __init__.py              # App factory, blueprint registration
├── domain/                  # Pipeline primitives, policy rules, validators
│   ├── pipeline.py          # PipelineContext, Stage, run_pipeline
│   └── policy.py            # Rule engine
├── workflows/
│   └── campaign.py          # Composed stages: validate → plan → draft → policy → insights → persist
├── services/
│   ├── planner.py
│   ├── drafter.py
│   └── persistence.py       # SQLAlchemy + SQLite
├── integrations/
│   └── openai_provider.py   # Real OpenAI + deterministic fallback
├── routes/
│   └── workflows.py
├── utils/
│   └── mock_data.json       # Demo input
└── container.py             # Provider wiring
tests/
└── test_workflow.py
```

---

## About AIGOS

AIGOS (Content Autopilot) is the production system this slice is extracted from — a multi-tenant SaaS for AI-driven content generation, lead discovery, and contractor operations. The live platform runs Python 3.12 / Flask / SQLAlchemy 2.0 / PostgreSQL / Redis / Celery on Railway, integrates OpenAI and a handful of social-media APIs, and is built around the same stage-based workflow architecture demonstrated here.

What's intentionally excluded from this repository: production prompts and prompt-tuning, multi-tenant data isolation, billing, authentication, background worker topology, and vendor credentials. See [`PORTFOLIO_SCOPE.md`](PORTFOLIO_SCOPE.md) and [`DISCLAIMER.md`](DISCLAIMER.md).

---

## Available on request

- Architecture walkthroughs of the production system
- Discussion of specific design decisions and the alternatives considered
- Sample production-shaped code under NDA

Reach me through the contact info on my [GitHub profile](https://github.com/nuccitech).

---

*MIT licensed. Code in this repository is portfolio-safe and contains no proprietary AIGOS logic.*
