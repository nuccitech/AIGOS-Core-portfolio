import re
import time
from typing import Any, Dict, List, Tuple

from webapp.integrations.ai_client import MockLLMClient
from webapp.integrations.photo_enhancement import MockPhotoEnhancement
from webapp.integrations.research_aggregator import MockResearchAggregator
from webapp.integrations.vision_service import MockVisionService
from webapp.models.schema import CampaignRequest, Photo, Post

CONTENT_TEMPLATES: Dict[int, str] = {
    1: "\n\n[STRUCTURE: Hook → Problem → Solution → CTA]",
    2: "\n\n[STRUCTURE: Story → Insight → Offer → CTA]",
    3: "\n\n[STRUCTURE: Stat → Context → Takeaway → CTA]",
}
CONTENT_TYPES = ["blog", "email", "social", "ad_copy"]
MAX_GENERATION_TIME = 60  # seconds; aborts the generation loop if exceeded


class ContentService:
    def __init__(self):
        self.llm = MockLLMClient()
        self.research_aggregator = MockResearchAggregator()
        self.vision_service = MockVisionService()
        self.photo_enhancement = MockPhotoEnhancement()

    # --- Stage 1: extract_urls ---

    def extract_urls(self, research_sources: str) -> List[str]:
        pattern = r"https?://[^\s\)\]\>\"']+"
        raw = re.findall(pattern, research_sources)
        cleaned = [url.rstrip(".,;:!?") for url in raw]
        return list(dict.fromkeys(cleaned))  # deduplicate, preserve order

    # --- Stage 2: aggregate_research ---

    def aggregate_research(
        self,
        topic: str,
        industry: str,
        user_urls: List[str],
    ) -> Dict[str, Any]:
        try:
            return self.research_aggregator.aggregate_research(
                topic=topic,
                industry=industry,
                user_urls=user_urls,
            )
        except Exception:
            return {"sources": [], "user_content": {}, "summary": "", "enhanced_context": ""}

    # --- Stage 3: apply_content_template ---

    def apply_content_template(self, research_sources: str, template_id: int) -> str:
        template = CONTENT_TEMPLATES.get(template_id)
        if template is None:
            return research_sources
        return research_sources + template

    # --- Stage 4: process_work_photos ---

    def process_work_photos(self, photos: List[Photo]) -> List[Dict[str, Any]]:
        enhanced = []
        for photo in photos:
            try:
                vision_result = (
                    self.vision_service.analyze_image(
                        image_source=photo.original_path,
                        context=photo.caption,
                    )
                    if photo.original_path
                    else {"success": False, "description": ""}
                )
                ai_description = (
                    vision_result["description"]
                    if vision_result.get("success")
                    else (photo.caption or "marketing asset")
                )
                enhanced_path = self.photo_enhancement.apply_text_overlay(
                    image_path=photo.original_path,
                    caption=photo.caption,
                )
                enhanced.append({
                    "original_path": photo.original_path,
                    "caption": photo.caption,
                    "enhanced_path": enhanced_path,
                    "enhancement_status": "completed",
                    "ai_description": ai_description,
                    "ai_analysis_status": "completed",
                })
            except Exception:
                # Graceful fallback: keep original photo, skip AI description
                enhanced.append({
                    "original_path": photo.original_path,
                    "caption": photo.caption,
                    "enhanced_path": photo.original_path,
                    "enhancement_status": "failed",
                    "ai_description": photo.caption or "marketing asset",
                    "ai_analysis_status": "skipped",
                })
        return enhanced

    # --- Stage 6: generate_hashtags ---

    def generate_hashtags(self, topic: str, niche: str, research_sources: str) -> str:
        try:
            return self.llm.generate_hashtags(topic=topic, niche=niche)
        except Exception:
            return "#content #marketing"

    # --- Stage 7: generate_posts_loop ---

    def generate_posts(
        self,
        request: CampaignRequest,
        enhanced_photos: List[Dict[str, Any]],
        hashtags: str,
        research_context: str,
    ) -> Tuple[List[Post], List[str]]:
        posts: List[Post] = []
        failed: List[str] = []
        content_types = request.custom_data.get("content_types", CONTENT_TYPES)
        tone = request.custom_data.get("brand_voice", "professional")
        start_time = time.time()

        for i in range(request.total_posts):
            if time.time() - start_time > MAX_GENERATION_TIME:
                failed.append(f"loop:timeout-after-{len(posts)}-posts")
                break

            content_type = content_types[i % len(content_types)]
            platform = request.target_platforms[i % len(request.target_platforms)]
            photo = enhanced_photos[i % len(enhanced_photos)] if enhanced_photos else None

            try:
                response = self.llm.generate_post(
                    topic=request.topic,
                    content_type=content_type,
                    platform=platform,
                    tone=tone,
                    research_context=research_context,
                    photo_description=photo["ai_description"] if photo else "",
                )
                posts.append(Post(
                    campaign_id=0,
                    post_type=content_type,
                    platform=platform,
                    caption=response["caption"],
                    content=response["content"],
                    hashtags=hashtags,
                    image_path=photo["enhanced_path"] if photo else "",
                    status="draft",
                ))
            except Exception as exc:
                failed.append(f"post_{i}:{exc}")

        return posts, failed
