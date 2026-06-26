from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from webapp.models.schema import CampaignRequest, Photo, PlatformRestriction, Post


@dataclass
class PipelineContext:
    request: CampaignRequest
    # stage: extract-urls
    extracted_urls: List[str] = field(default_factory=list)
    # stage: aggregate-research
    research: Dict[str, Any] = field(default_factory=dict)
    # stage: process-work-photos
    enhanced_photos: List[Dict[str, Any]] = field(default_factory=list)
    # stage: check-platform-restrictions
    platform_restrictions: Optional[PlatformRestriction] = None
    # stage: generate-hashtags
    hashtags: str = ""
    # stage: generate-posts
    posts: List[Post] = field(default_factory=list)
    failed_pieces: List[str] = field(default_factory=list)
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
