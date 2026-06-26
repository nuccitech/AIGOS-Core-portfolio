from dataclasses import asdict

from webapp.domain.pipeline import PipelineContext, PipelineStage
from webapp.domain.validators import validate_campaign_request
from webapp.services.content_service import ContentService
from webapp.services.policy_service import PolicyService
from webapp.services.storage_service import MockStorageService


class ValidateStage(PipelineStage):
    name = "validate-request"

    def run(self, context: PipelineContext) -> None:
        issues = validate_campaign_request(context.request)
        if issues:
            raise ValueError({"validation_errors": issues})


class ExtractUrlsStage(PipelineStage):
    """Stage 1 — extract_urls: parse and deduplicate valid HTTP/HTTPS URLs."""

    name = "extract-urls"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        context.extracted_urls = self.content_service.extract_urls(
            context.request.research_sources
        )
        context.trace.append(f"urls-found:{len(context.extracted_urls)}")


class AggregateResearchStage(PipelineStage):
    """Stage 2 — aggregate_research: merge external web content with user-supplied context."""

    name = "aggregate-research"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        try:
            context.research = self.content_service.aggregate_research(
                topic=context.request.topic,
                industry=context.request.industry,
                user_urls=context.extracted_urls,
            )
            enhanced = context.research.get("enhanced_context", "")
            if enhanced:
                context.request.research_sources = (
                    context.request.research_sources + "\n\n" + enhanced
                )
        except Exception:
            # Fallback: proceed with original research_sources only
            context.trace.append("research-aggregation:fallback")


class ApplyTemplateStage(PipelineStage):
    """Stage 3 — apply_content_template: inject structural template into research context."""

    name = "apply-content-template"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        tid = context.request.template_id
        if tid is None:
            return
        context.request.research_sources = self.content_service.apply_content_template(
            context.request.research_sources, tid
        )


class ProcessPhotosStage(PipelineStage):
    """Stage 4 — process_work_photos: vision analysis + enhancement; falls back to original on error."""

    name = "process-work-photos"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        if not context.request.uploaded_photos:
            return
        context.enhanced_photos = self.content_service.process_work_photos(
            context.request.uploaded_photos
        )
        context.trace.append(f"photos-enhanced:{len(context.enhanced_photos)}")


class CheckPlatformRestrictionsStage(PipelineStage):
    """Stage 5 — check_platform_restrictions: enforce industry compliance; route away from restricted platforms."""

    name = "check-platform-restrictions"

    def __init__(self, policy_service: PolicyService):
        self.policy_service = policy_service

    def run(self, context: PipelineContext) -> None:
        context.platform_restrictions = self.policy_service.check_platform_restrictions(
            industry=context.request.industry,
            target_platforms=context.request.target_platforms,
        )
        for warning in context.platform_restrictions.warnings:
            context.trace.append(f"restriction:{warning}")
        # Route posts away from restricted platforms
        allowed = context.platform_restrictions.allowed_platforms
        if allowed:
            context.request.target_platforms = allowed


class GenerateHashtagsStage(PipelineStage):
    """Stage 6 — generate_hashtags: centralised hashtag block shared across all posts."""

    name = "generate-hashtags"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        context.hashtags = self.content_service.generate_hashtags(
            topic=context.request.topic,
            niche=context.request.niche,
            research_sources=context.request.research_sources,
        )


class GeneratePostsStage(PipelineStage):
    """Stage 7 — generate_posts_loop: iterate total_posts, cycling content types and platforms."""

    name = "generate-posts"

    def __init__(self, content_service: ContentService):
        self.content_service = content_service

    def run(self, context: PipelineContext) -> None:
        research_context = context.research.get(
            "enhanced_context", context.request.research_sources
        )
        posts, failed = self.content_service.generate_posts(
            request=context.request,
            enhanced_photos=context.enhanced_photos,
            hashtags=context.hashtags,
            research_context=research_context,
        )
        context.posts = posts
        context.failed_pieces = failed
        context.trace.append(f"posts-generated:{len(posts)}")
        if failed:
            context.trace.append(f"posts-failed:{len(failed)}")


class PersistStage(PipelineStage):
    """Persist generated posts to storage (MockStorageService → S3StorageService in production)."""

    name = "persist"

    def __init__(self, storage: MockStorageService):
        self.storage = storage

    def run(self, context: PipelineContext) -> None:
        payload = {
            "posts": [asdict(p) for p in context.posts],
            "hashtags": context.hashtags,
        }
        result = self.storage.save(payload)
        context.trace.append(f"storage:{result['status']}")
