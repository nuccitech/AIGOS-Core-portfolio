from dataclasses import asdict
from typing import Dict

from webapp.domain.pipeline import PipelineContext, PipelineStage
from webapp.domain.validators import validate_campaign_request
from webapp.services.analytics_service import AnalyticsService
from webapp.services.content_service import ContentService
from webapp.services.storage_service import MockStorageService


class ValidateStage(PipelineStage):
    name = "validate-request"

    def run(self, context: PipelineContext) -> None:
        issues = validate_campaign_request(context.request)
        if issues:
            raise ValueError({"validation_errors": issues})


class PlanStage(PipelineStage):
    name = "plan"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        context.plan = self.content_service.build_plan(context.request)


class DraftStage(PipelineStage):
    name = "draft"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        drafts_bundle = self.content_service.generate_drafts(context.request)
        context.drafts = drafts_bundle["drafts"]
        context.prompt_example = drafts_bundle["prompt"]
        context.trace.append("prompt-example:stored")


class InsightsStage(PipelineStage):
    name = "insights"

    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics

    def run(self, context: PipelineContext) -> None:
        context.insights = self.analytics.enrich(context.request)


class PersistStage(PipelineStage):
    name = "persist"

    def __init__(self, storage: MockStorageService):
        self.storage = storage

    def run(self, context: PipelineContext) -> None:
        payload: Dict[str, object] = {
            "plan": asdict(context.plan) if context.plan else {},
            "drafts": [asdict(draft) for draft in context.drafts],
            "insights": context.insights,
        }
        storage_result = self.storage.save(payload)
        context.trace.append(f"storage:{storage_result['status']}")
