from typing import Any, Dict, List, Protocol

from webapp.models.schema import CampaignRequest, Photo, PlatformRestriction, Post


class LLMClient(Protocol):
    def generate_post(
        self,
        topic: str,
        content_type: str,
        platform: str,
        tone: str,
        research_context: str,
        photo_description: str,
    ) -> Dict[str, str]: ...

    def generate_hashtags(self, topic: str, niche: str) -> str: ...


class ResearchAggregatorProtocol(Protocol):
    def aggregate_research(
        self,
        topic: str,
        industry: str,
        max_sources: int,
        recency_days: int,
        include_sources: List[str],
        user_urls: List[str],
    ) -> Dict[str, Any]: ...


class VisionServiceProtocol(Protocol):
    def analyze_image(
        self,
        image_source: str,
        context: str,
        detail_level: str,
    ) -> Dict[str, Any]: ...


class PhotoEnhancementProtocol(Protocol):
    def apply_text_overlay(
        self,
        image_path: str,
        business_name: str,
        caption: str,
        industry: str,
        brand_voice: str,
        platform: str,
        text_color: str,
    ) -> str: ...


class StorageProvider(Protocol):
    def save(self, item: Dict[str, object]) -> Dict[str, object]: ...
