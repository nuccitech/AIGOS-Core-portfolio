from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Photo:
    original_path: str
    caption: str = ""
    s3_url: str = ""
    enhanced_path: str = ""
    enhancement_status: str = "pending"
    ai_description: str = ""
    ai_analysis_status: str = "pending"


@dataclass
class Post:
    campaign_id: int
    post_type: str  # 'blog', 'email', 'social', 'ad_copy'
    platform: str
    caption: str
    content: str
    hashtags: str = ""
    image_path: str = ""
    status: str = "draft"


@dataclass
class ContentItem:
    content_type: str
    title: str
    content: str
    meta_description: str = ""
    keywords: str = ""
    status: str = "draft"
    word_count: int = 0


@dataclass
class PlatformRestriction:
    allowed_platforms: List[str]
    restricted_platforms: List[str]
    warnings: List[str]


@dataclass
class CampaignRequest:
    topic: str
    niche: str
    industry: str
    research_sources: str = ""
    target_platforms: List[str] = field(default_factory=lambda: ["instagram", "facebook"])
    total_posts: int = 5
    template_id: Optional[int] = None
    uploaded_photos: List[Photo] = field(default_factory=list)
    # custom_data mirrors the campaign.custom_data JSON column in production
    custom_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CampaignRequest":
        photos = [
            Photo(**p) if isinstance(p, dict) else p
            for p in payload.get("uploaded_photos", [])
        ]
        return cls(
            topic=payload.get("topic", ""),
            niche=payload.get("niche", ""),
            industry=payload.get("industry", ""),
            research_sources=payload.get("research_sources", ""),
            target_platforms=payload.get("target_platforms", ["instagram", "facebook"]),
            total_posts=payload.get("total_posts", 5),
            template_id=payload.get("template_id"),
            uploaded_photos=photos,
            custom_data=payload.get("custom_data", {}),
        )
