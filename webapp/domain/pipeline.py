from dataclasses import dataclass, field
from typing import Dict, List, Optional

from webapp.models.schema import CampaignPlan, CampaignRequest, DraftContent
from webapp.domain.policies import PolicyDecision


@dataclass
class PipelineContext:
    request: CampaignRequest
    plan: Optional[CampaignPlan] = None
    drafts: List[DraftContent] = field(default_factory=list)
    insights: Dict[str, str] = field(default_factory=dict)
    prompt_example: Optional[str] = None
    policy: Optional[PolicyDecision] = None
    trace: List[str] = field(default_factory=list)


class PipelineStage:
    name = "unnamed-stage"

    def run(self, context: PipelineContext) -> None:
        raise NotImplementedError


class Pipeline:
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages

    def run(self, context: PipelineContext) -> PipelineContext:
        for stage in self.stages:
            context.trace.append(f"stage:{stage.name}")
            stage.run(context)
        return context
