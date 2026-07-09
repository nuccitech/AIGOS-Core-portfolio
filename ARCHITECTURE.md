# Architecture & Design Decisions

This document walks through the central design decision in this repository — how the campaign workflow is structured — including the alternatives that were considered and the tradeoffs accepted. It's the kind of decision that doesn't show up in a `tree` listing but determines how the system feels to extend a year in.

## The pipeline-as-composable-stages pattern

The campaign workflow runs through a list of stages: validate-request → extract-urls → aggregate-research → apply-content-template → process-work-photos → check-platform-restrictions → generate-hashtags → generate-posts → persist. Each stage is a small class that takes the shared `PipelineContext`, does its work, and mutates the context in place. The runner threads the context through them in order and records each stage in a `trace`.

```python
class PipelineStage:
    name = "unnamed-stage"

    def run(self, context: PipelineContext) -> None:
        raise NotImplementedError
```

Stages don't import each other. They communicate only through fields they read and write on the context. The runner enforces ordering and appends the trace. This is the structure in `webapp/domain/pipeline.py`; the concrete stages live in `webapp/workflows/stages.py` and are composed into the pipeline in `webapp/workflows/campaign_workflow.py`.

### Why not just one service method?

The obvious alternative — and what the workflow looked like for the first ~6 weeks in production — is a single `CampaignService.generate(brief)` method that does everything inline. It's simpler. There's no framework. The control flow is obvious from top to bottom.

It broke down for three reasons.

**Testing got expensive.** To unit-test the platform-restriction logic I had to stub out the entire content-generation chain, which meant either heavy mock setup per test or carving the policy code out and testing it separately — at which point I'd done half the refactor anyway. With composable stages, each stage's unit tests just construct the inputs it needs and assert on the result. The full-pipeline test runs the real runner with mock providers injected through the container.

**Partial reruns weren't natural.** In production, a meaningful share of campaigns needed a re-generation with adjusted constraints. With the monolithic version, re-generating meant either re-running the whole method (wasteful — the brief was already valid, the research was still good) or carving out a separate `regenerate()` method that duplicated half the original code. With stages, the earlier context is reused and only the later stages replay.

**New stages required surgery.** When photo processing was added, the monolithic version touched the main method, the response shape, the test suite, and the error handling. With the stage list it's a single entry in `webapp/workflows/campaign_workflow.py` and a new class in `webapp/workflows/stages.py`.

### What this costs

There's no free lunch. The stage abstraction adds friction in three places that matter:

**Indirection on read.** A reader following a request through the system now has to open the runner, then the workflow definition, then the stage. For a small workflow this is more files for the same logic. The honest answer is the indirection is only worth it once you have either (a) more than ~4 stages, or (b) a real reason to want stage-level testing or replay. For a smaller workflow you'd skip this and write a service method.

**Context shape sprawl.** `PipelineContext` accumulates fields as the pipeline progresses (`extracted_urls`, `research`, `enhanced_photos`, `platform_restrictions`, `hashtags`, `posts`...). It's tempting to make every field optional, which then leaves later stages defensively checking whether earlier ones ran. Here I kept a simple dataclass with sensible empty defaults to keep the cognitive load low — flagging this as an explicit tradeoff rather than an oversight.

**Ordering is implicit.** The runner enforces *that* stages run in order, not *which* order makes sense. Putting `persist` before `generate-posts` would happily run and store an empty campaign. In production this is caught by a topology check where each stage declares its inputs; here it's caught by tests (`test_trace_records_all_stage_names`).

### Where the production version diverges

A few places where this slice intentionally simplifies what the production system does:

- **Stages declare inputs/outputs.** Production stages have a `requires`/`produces` declaration that the runner validates at startup, catching "I added a stage but forgot to wire it" before it hits a request. Not included here because it adds real surface for a benefit that's only obvious at scale.
- **Stages are tenant-aware.** The production `PipelineContext` carries a `tenant_id` and stages route through tenant-scoped repositories. Stripped here because the multi-tenant logic isn't in this repository.
- **Providers are real.** Here every integration (`webapp/integrations/`) is a deterministic mock that names the production component it stands in for. Production wires in the real LLM, research, vision, and storage providers through the same `ServiceContainer` seam.

## A smaller decision worth flagging: deterministic mock providers

Every external provider in this slice is a deterministic mock, injected through `webapp/container.py`. This wasn't just to make demos cheap — it's because a workflow that requires paid API keys to run any tests is a workflow that doesn't get tested. The whole pipeline is exercised offline by the test suite. The seam is the same one production uses to swap between OpenAI, Bedrock, and a recorded-response cache used during development: the stages depend on the interfaces in `webapp/domain/interfaces.py`, not on any concrete provider, so swapping implementations never touches stage code.

## Things I'd change if starting over

- I'd give `PipelineContext` typed per-stage outputs rather than one flat dataclass with empty defaults; the "did this stage run?" checks add up.
- The policy/restriction rules accumulated configuration faster than their schema; I'd treat rule configuration as code from day one.
- Tracing went in late. Starting with structured logging at the stage boundary from day one would have saved a real chunk of debugging time later.

---

*This document covers one repository. Architectural decisions for the broader AIGOS platform — multi-tenancy, async worker topology, the Celery priority queue layout, the AWS Lambda + Bedrock generation path — are available for discussion on request.*
