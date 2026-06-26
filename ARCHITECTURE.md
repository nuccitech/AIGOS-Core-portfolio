# Architecture & Design Decisions

This document walks through the central design decision in this repository — how the campaign workflow is structured — including the alternatives that were considered and the tradeoffs accepted. It's the kind of decision that doesn't show up in a `tree` listing but determines how the system feels to extend a year in.

## The pipeline-as-composable-stages pattern

The campaign workflow runs through six stages: validate → plan → draft → policy → insights → persist. Each stage is a callable that takes a `PipelineContext` and returns a `StageResult`. The runner threads context through them in order and stops on a hard reject.

```python
class Stage(Protocol):
    name: str
    def run(self, ctx: PipelineContext) -> StageResult: ...
```

Stages don't import each other. They communicate only through fields they write onto the context. The runner enforces ordering and handles the error envelope. This is the structure in `webapp/domain/pipeline.py` and `webapp/workflows/campaign.py`.

### Why not just one service method?

The obvious alternative — and what the workflow looked like for the first ~6 weeks in production — is a single `CampaignService.generate(brief)` method that does everything inline. It's simpler. There's no framework. The control flow is obvious from top to bottom.

It broke down for three reasons.

**Testing got expensive.** To unit-test the policy logic I had to stub out the entire OpenAI call chain, which meant either heavy mock setup per test or carving the policy code out and testing it separately — at which point I'd done half the refactor anyway. With composable stages, each stage's unit tests just construct a `PipelineContext` with the inputs it needs and assert on the result. The full-pipeline test uses a fake LLM provider injected through the container.

**Partial reruns weren't natural.** In production, ~12% of campaigns failed policy on first generation and needed a re-draft with adjusted constraints. With the monolithic version, re-drafting meant either re-running the whole pipeline (wasteful — the brief was already valid, the plan was still good) or carving out a separate `redraft()` method that duplicated half the original code. With stages, the existing context is replayed from the `draft` stage onward.

**New stages required surgery.** When the insights stage was added, the monolithic version touched the main method, the response shape, the test suite, and the error handling. With the stage list it's a single line in `webapp/workflows/campaign.py` and a new file in `webapp/domain/`.

### What this costs

There's no free lunch. The stage abstraction adds friction in three places that matter:

**Indirection on read.** A reader following a request through the system now has to open the runner, then the workflow definition, then the stage. For a small workflow this is more files for the same logic. The honest answer is the indirection is only worth it once you have either (a) more than ~4 stages, or (b) a real reason to want stage-level testing or replay. For a smaller workflow you'd skip this and write a service method.

**Context shape sprawl.** `PipelineContext` accumulates fields as the pipeline progresses (`brief`, `plan`, `drafts`, `policy_result`, `insights`...). It's tempting to make it a typed dataclass with every field optional, which then leaves every reader writing `if ctx.plan is not None` everywhere. The production version solved this with a discriminated union per stage output, but for the portfolio slice I kept the simpler `Optional` dataclass to keep the cognitive load low — flagging this as an explicit tradeoff rather than an oversight.

**Ordering is implicit.** The runner enforces *that* stages run in order, not *which* order makes sense. Putting `persist` before `policy` would happily compile and run and store rejected drafts in the database. In production this is caught by a topology check that each stage declares its inputs; here it's caught by tests.

### Where the production version diverges

A few places where this slice intentionally simplifies what the production system does:

- **Stages declare inputs/outputs.** Production stages have a `requires` and `produces` declaration that the runner validates at startup. This catches "I added a stage but forgot to update the wiring" before it hits a request. Not included here because it adds ~80 lines for a benefit that's only obvious at scale.
- **Stages are tenant-aware.** The production `PipelineContext` carries a `tenant_id` and stages route through tenant-scoped repositories. Stripped here because the multi-tenant logic isn't in the repository.
- **Failures are categorized.** Production splits `StageResult` failure modes into `retryable`, `user_error`, and `system_error`, which the runner uses to decide whether to enqueue a retry, surface a 4xx, or page on-call. Here it's a single `ok/failed` boolean.

## A smaller decision worth flagging: deterministic fallback for drafting

The `draft` stage uses real OpenAI when `OPENAI_API_KEY` is set and falls back to a deterministic template otherwise. This wasn't to be impressive in demos — it's because a workflow that requires a paid API key to run any tests is a workflow that doesn't get tested. The fallback path is exercised by the test suite; the OpenAI path is exercised by integration tests that are skipped without the env var. In production the same toggle pattern is used to swap between OpenAI, Bedrock, and a recorded-response cache used during development.

## Things I'd change if starting over

- I'd start with the typed discriminated union for stage outputs rather than the optional-fields context. The migration later wasn't free.
- The policy rule engine accumulated configuration in a YAML file that grew faster than its schema; I'd treat rule configuration as code from day one.
- Tracing went in late. Starting with structured logging at the stage boundary from day one would have saved a real chunk of debugging time later.

---

*This document covers one repository. Architectural decisions for the broader AIGOS platform — multi-tenancy, async worker topology, the Celery priority queue layout, the Lambda + Bedrock generation path — are available for discussion on request.*
