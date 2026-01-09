from dataclasses import asdict
from typing import Dict

from webapp.domain.pipeline import Pipeline, PipelineContext
from webapp.models.schema import CampaignRequest
from webapp.services.analytics_service import AnalyticsService
from webapp.services.content_service import ContentService
from webapp.services.storage_service import MockStorageService
from webapp.workflows.stages import (
    DraftStage,
    InsightsStage,
    PersistStage,
    PlanStage,
    ValidateStage,
)


class CampaignWorkflow:
    def __init__(self, enable_insights: bool = True, enable_persistence: bool = True):
        content_service = ContentService()
        analytics_service = AnalyticsService()
        storage_service = MockStorageService()
        stages = [
            ValidateStage(),
            PlanStage(content_service),
            DraftStage(content_service),
        ]
        if enable_insights:
            stages.append(InsightsStage(analytics_service))
        if enable_persistence:
            stages.append(PersistStage(storage_service))
        self.pipeline = Pipeline(stages)

    def run(self, request: CampaignRequest) -> Dict[str, object]:
        context = PipelineContext(request=request)
        self.pipeline.run(context)
        draft_payload = [asdict(draft) for draft in context.drafts]
        return {
            "plan": asdict(context.plan) if context.plan else {},
            "drafts": draft_payload,
            "insights": context.insights,
            "prompt_example": context.prompt_example,
            "trace": context.trace,
        }
