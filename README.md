# AIGOS — Campaign Workflow (Portfolio Slice)

A focused, runnable slice of [AIGOS (Content Autopilot)](#about-aigos), the production multi-tenant SaaS I built solo. This repository extracts one production workflow — the campaign content-generation pipeline — and runs it end-to-end with real validation, a real stage-based pipeline runner, real policy/compliance logic, and an explicit service/provider architecture.

This is **not** a stripped-down marketing tour. The pipeline you see here is the same shape and structure used in production, with proprietary prompts, tenant logic, and vendor integrations removed. Every external provider (LLM, research aggregation, vision, photo enhancement, storage) is replaced with a **deterministic mock** so the whole thing runs offline with no API keys — the mock classes name the production component they stand in for. Everything that *is* in this repo is real, non-trivial code.

---

## What's actually in here

The campaign workflow composes nine stages. The runner threads a `PipelineContext` through them in order, appending to a `trace` as it goes; validation failures short-circuit with a structured 400.

| Stage (`name`) | What it does | Implementation |
|---|---|---|
| `validate-request` | Required-field validation of the campaign brief (topic, niche, industry, platforms, post count) | `validate_campaign_request`; raises → HTTP 400 with per-field reasons |
| `extract-urls` | Parses and de-duplicates HTTP/HTTPS URLs from the research sources | Regex + order-preserving dedupe |
| `aggregate-research` | Merges user-supplied URLs and context into an enhanced research blob | `MockResearchAggregator` (production: web scrape + summarize) |
| `apply-content-template` | Injects a structural template into the research context | Template map keyed by `template_id` |
| `process-work-photos` | Vision analysis + text-overlay enhancement per photo, with graceful fallback | `MockVisionService` + `MockPhotoEnhancement` |
| `check-platform-restrictions` | Industry compliance: routes away from restricted platforms and emits warnings | `PolicyService` rule map |
| `generate-hashtags` | One shared hashtag block for the whole campaign | `MockLLMClient` |
| `generate-posts` | Loops `total_posts`, cycling content types and platforms, with per-item failure isolation and a time budget | `MockLLMClient` |
| `persist` | Writes posts + hashtags to storage | `MockStorageService` (in-memory; production: S3) |

Each stage is an independent unit that reads and writes the shared context; stages never import each other. See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the design rationale and tradeoffs.

Alongside the pipeline, the app exposes a small mocked surface: `GET /api/health`, `GET /api/docs`, and `GET /api/insights/overview` (sample analytics — not part of the pipeline).

---

## Quick demo

No API key is required — all providers are mocked, so the pipeline runs offline and deterministically.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

In another shell, run a valid campaign brief:

```bash
curl -X POST http://127.0.0.1:5000/api/workflows/campaign \
  -H "Content-Type: application/json" \
  -d @webapp/utils/mock_data.json
```

The response is the full pipeline trace — every stage name, the extracted URLs, the research summary, the generated posts, and the storage result — not a canned payload.

![Example response from the campaign workflow endpoint](assets/quick-demo.svg)

Now send a deliberately invalid brief to see the validation rejection:

```bash
curl -X POST http://127.0.0.1:5000/api/workflows/campaign \
  -H "Content-Type: application/json" \
  -d @webapp/utils/mock_data_bad.json
```

This returns **HTTP 400** with structured, per-field reasons:

```json
{
  "error": "validation_failed",
  "details": {
    "validation_errors": [
      "topic is required.",
      "niche is required.",
      "industry is required.",
      "At least one target_platform is required.",
      "total_posts must be at least 1."
    ]
  }
}
```

---

## Architecture in one paragraph

Stages are independent units that take a `PipelineContext` and mutate it; the `Pipeline` runner in `webapp/domain/pipeline.py` handles ordering and tracing. Routes stay thin (parse request → run the workflow → return result). Services hold the business logic, and providers are wired through a small `ServiceContainer` (`webapp/container.py`) so each mock integration can be swapped for its production implementation without touching the stages. State flows explicitly through the context; nothing reaches into globals. The composed stage list lives in `webapp/workflows/campaign_workflow.py`, with the stage classes in `webapp/workflows/stages.py`. The detailed rationale (why stages over a single service method, where this simplifies vs. production) is in [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers the validator, the URL extractor, the template and photo stages, the platform-restriction policy, hashtag generation and its fallback, the post-shape contract, a full pipeline run, and the HTTP routes (200 and 400 paths).

---

## Directory layout

```
app.py                          # Entry point (create_app + dev server)
webapp/
├── __init__.py                 # App factory, blueprint registration
├── container.py                # ServiceContainer + provider wiring
├── config/
│   ├── base.py                 # Config (MOCK_MODE)
│   └── feature_flags.py        # ENABLE_PERSISTENCE
├── domain/
│   ├── pipeline.py             # PipelineContext, PipelineStage, Pipeline runner
│   ├── interfaces.py           # Protocols for swappable providers
│   ├── validators.py           # validate_campaign_request
│   └── policies.py             # PolicyDecision
├── models/
│   └── schema.py               # CampaignRequest, Post, Photo, PlatformRestriction (dataclasses)
├── workflows/
│   ├── campaign_workflow.py    # Composes the stages into the pipeline
│   └── stages.py               # Stage classes (validate → ... → persist)
├── services/
│   ├── content_service.py      # URL extract, research, template, photos, hashtags, posts
│   ├── policy_service.py       # Platform-restriction checks
│   ├── storage_service.py      # MockStorageService (in-memory)
│   ├── analytics_service.py    # Mock insights
│   └── workflow_orchestrator.py
├── integrations/               # Deterministic mocks for external providers
│   ├── ai_client.py            # MockLLMClient (production: TrackedOpenAI)
│   ├── research_aggregator.py
│   ├── vision_service.py
│   └── photo_enhancement.py
├── routes/
│   ├── workflows.py            # POST /api/workflows/campaign
│   ├── insights.py             # GET  /api/insights/overview
│   ├── health.py               # GET  /api/health
│   └── docs.py                 # GET  /api/docs
├── prompts/
│   └── example_prompts.py      # Portfolio-safe example prompt template
└── utils/
    ├── logger.py
    ├── mock_data.json          # Valid demo input → full pipeline trace
    └── mock_data_bad.json      # Invalid input → 400 with structured reasons
tests/
├── test_campaign_workflow.py   # Stage + full-pipeline tests
└── test_routes.py              # HTTP route tests
```

---

## About AIGOS

AIGOS (Content Autopilot) is the production system this slice is extracted from — a multi-tenant SaaS for AI-driven content generation, lead discovery, and business research. The live platform runs Python 3.12 / Flask / SQLAlchemy 2.0 / PostgreSQL / Redis / Celery, deployed on AWS (EC2, RDS, ElastiCache, S3, with CodeDeploy), integrates OpenAI and a handful of social-media APIs, and is built around the same stage-based workflow architecture demonstrated here.

What's intentionally excluded from this repository: production prompts and prompt-tuning, multi-tenant data isolation, billing, authentication, background worker topology, real vendor integrations, and credentials. See [`PORTFOLIO_SCOPE.md`](PORTFOLIO_SCOPE.md) and [`DISCLAIMER.md`](DISCLAIMER.md).

---

## Available on request

- Architecture walkthroughs of the production system
- Discussion of specific design decisions and the alternatives considered
- Sample production-shaped code under NDA

Reach me through the contact info on my [GitHub profile](https://github.com/nuccitech).

---

*MIT licensed. Code in this repository is portfolio-safe and contains no proprietary AIGOS logic.*
