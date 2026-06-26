# Portfolio Scope

This repository is intentionally narrow. It extracts one production workflow — the campaign generation pipeline — from AIGOS (Content Autopilot), the multi-tenant SaaS platform it's part of. The code in this repo is real and runnable, but it is one slice of the larger system. See the [README](README.md) for what this slice demonstrates and [ARCHITECTURE.md](ARCHITECTURE.md) for the design rationale.

## What this repository includes

- The campaign workflow pipeline (validate → plan → draft → policy → insights → persist)
- Real validation, real policy rule engine, real persistence
- An OpenAI integration with a deterministic fallback so the pipeline runs without an API key
- A pytest suite that exercises each stage in isolation and the full pipeline end-to-end

## What is intentionally excluded

- Production prompts and prompt-tuning logic
- Multi-tenant data isolation, tenant resolution middleware, and tenant-scoped repositories
- Authentication, session management, and the Two-Factor Auth flow
- Billing and Stripe integrations
- The Celery worker topology, beat scheduler, and queue routing
- The AWS Lambda + Bedrock generation path (Stable Diffusion 3.5, Gemma)
- Vendor credentials and production configuration

## Available on request

- Architecture walkthroughs of the production system
- Design rationale for specific decisions and the alternatives considered
- Discussion of production tradeoffs and scaling considerations

Reach me through the contact info on my [GitHub profile](https://github.com/nuccitech).
