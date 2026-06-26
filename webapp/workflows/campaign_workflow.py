from dataclasses import asdict
from typing import Dict

from webapp.container import ServiceContainer
from webapp.domain.pipeline import Pipeline, PipelineContext
from webapp.models.schema import CampaignRequest
from webapp.workflows.stages import (
    ApplyTemplateStage,
    AggregateResearchStage,
    CheckPlatformRestrictionsStage,
    ExtractUrlsStage,
    GenerateHashtagsStage,
    GeneratePostsStage,
    PersistStage,
    ProcessPhotosStage,
    ValidateStage,
)


class CampaignWorkflow:
    def __init__(
        self,
        container: ServiceContainer,
        enable_persistence: bool = True,
    ):
        stages = [
            ValidateStage(),
            ExtractUrlsStage(container.content),
            AggregateResearchStage(container.content),
            ApplyTemplateStage(container.content),
            ProcessPhotosStage(container.content),
            CheckPlatformRestrictionsStage(container.policy),
            GenerateHashtagsStage(container.content),
            GeneratePostsStage(container.content),
        ]
        if enable_persistence:
            stages.append(PersistStage(container.storage))
        self.pipeline = Pipeline(stages)

    def run(self, request: CampaignRequest) -> Dict[str, object]:
        context = PipelineContext(request=request)
        self.pipeline.run(context)
        return {
            "platform_restrictions": (
                asdict(context.platform_restrictions)
                if context.platform_restrictions
                else {}
            ),
            "hashtags": context.hashtags,
            "posts": [asdict(p) for p in context.posts],
            "research_summary": context.research.get("summary", ""),
            "extracted_urls": context.extracted_urls,
            "enhanced_photos": context.enhanced_photos,
            "failed_pieces": context.failed_pieces,
            "trace": context.trace,
        }
