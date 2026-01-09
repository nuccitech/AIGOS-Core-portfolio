from dataclasses import asdict
from typing import Dict

from webapp.domain.pipeline import Pipeline, PipelineContext
from webapp.models.schema import CampaignRequest
from webapp.container import ServiceContainer
from webapp.workflows.stages import (
    DraftStage,
    InsightsStage,
    PersistStage,
    PlanStage,
    PolicyStage,
    ValidateStage,
)


class CampaignWorkflow:
    def __init__(
        self,
        container: ServiceContainer,
        enable_insights: bool = True,
        enable_persistence: bool = True,
    ):
        stages = [
            ValidateStage(),
            PlanStage(container.content),
            DraftStage(container.content),
            PolicyStage(container.policy),
        ]
        if enable_insights:
            stages.append(InsightsStage(container.analytics))
        if enable_persistence:
            stages.append(PersistStage(container.storage))
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
            "policy": asdict(context.policy) if context.policy else {},
            "trace": context.trace,
        }
