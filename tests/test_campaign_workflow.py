import pytest

from webapp.models.schema import CampaignRequest, Photo
from webapp.services.content_service import ContentService
from webapp.services.policy_service import PolicyService, REGULATED_INDUSTRIES
from webapp.services.workflow_orchestrator import WorkflowOrchestrator


def _request(**kwargs) -> CampaignRequest:
    defaults = dict(
        topic="Emergency Plumbing",
        niche="home-services",
        industry="plumbing",
        research_sources="See https://example.com/tips for context.",
        target_platforms=["instagram", "facebook"],
        total_posts=3,
    )
    defaults.update(kwargs)
    return CampaignRequest(**defaults)


# --- Pipeline integration ---

def test_workflow_returns_expected_keys():
    result = WorkflowOrchestrator().run_campaign(_request())
    for key in ("platform_restrictions", "hashtags", "posts", "trace",
                "research_summary", "extracted_urls", "enhanced_photos", "failed_pieces"):
        assert key in result


def test_posts_count_matches_total_posts():
    result = WorkflowOrchestrator().run_campaign(_request(total_posts=4))
    assert len(result["posts"]) == 4


def test_trace_records_all_stage_names():
    result = WorkflowOrchestrator().run_campaign(_request())
    stage_entries = [t for t in result["trace"] if t.startswith("stage:")]
    for stage in (
        "stage:extract-urls",
        "stage:aggregate-research",
        "stage:apply-content-template",
        "stage:process-work-photos",
        "stage:check-platform-restrictions",
        "stage:generate-hashtags",
        "stage:generate-posts",
    ):
        assert stage in stage_entries


def test_validation_raises_on_missing_topic():
    with pytest.raises(ValueError):
        WorkflowOrchestrator().run_campaign(
            CampaignRequest(topic="", niche="home-services", industry="plumbing")
        )


# --- Stage 1: extract_urls ---

def test_extract_urls_finds_http_and_https():
    svc = ContentService()
    urls = svc.extract_urls("Visit https://example.com and http://other.org/path for info.")
    assert "https://example.com" in urls
    assert "http://other.org/path" in urls


def test_extract_urls_deduplicates():
    svc = ContentService()
    urls = svc.extract_urls("https://a.com https://a.com https://b.com")
    assert urls.count("https://a.com") == 1


def test_extract_urls_strips_trailing_punctuation():
    svc = ContentService()
    urls = svc.extract_urls("Read this: https://example.com/guide.")
    assert "https://example.com/guide" in urls
    assert "https://example.com/guide." not in urls


def test_extract_urls_empty_on_no_urls():
    svc = ContentService()
    assert svc.extract_urls("No links here at all.") == []


def test_urls_appear_in_result():
    result = WorkflowOrchestrator().run_campaign(
        _request(research_sources="See https://example.com for context.")
    )
    assert "https://example.com" in result["extracted_urls"]


# --- Stage 3: apply_content_template ---

def test_template_appended_to_research_sources():
    svc = ContentService()
    result = svc.apply_content_template("Base context.", template_id=1)
    assert result.startswith("Base context.")
    assert "[STRUCTURE:" in result


def test_invalid_template_id_returns_original():
    svc = ContentService()
    assert svc.apply_content_template("Base context.", template_id=999) == "Base context."


# --- Stage 4: process_work_photos ---

def test_photo_processing_returns_one_entry_per_photo():
    svc = ContentService()
    photos = [Photo(original_path="img1.jpg", caption="Job site"), Photo(original_path="img2.jpg")]
    enhanced = svc.process_work_photos(photos)
    assert len(enhanced) == 2


def test_photo_with_empty_path_falls_back_to_caption():
    svc = ContentService()
    photo = Photo(original_path="", caption="Before and after repair")
    enhanced = svc.process_work_photos([photo])
    assert enhanced[0]["ai_description"] == "Before and after repair"


def test_photo_with_no_caption_falls_back_to_default():
    svc = ContentService()
    photo = Photo(original_path="", caption="")
    enhanced = svc.process_work_photos([photo])
    assert enhanced[0]["ai_description"] == "marketing asset"


# --- Stage 5: check_platform_restrictions ---

def test_unknown_industry_permits_all_platforms():
    svc = PolicyService()
    result = svc.check_platform_restrictions(
        industry="totally_unknown", target_platforms=["instagram", "facebook"]
    )
    assert result.allowed_platforms == ["instagram", "facebook"]
    assert result.restricted_platforms == []
    assert result.warnings == []


def test_regulated_industry_blocks_restricted_platform():
    if not REGULATED_INDUSTRIES:
        pytest.skip("No regulated industries defined in portfolio mock.")
    industry = next(iter(REGULATED_INDUSTRIES))
    restricted = REGULATED_INDUSTRIES[industry]["restricted_platforms"][0]
    svc = PolicyService()
    result = svc.check_platform_restrictions(
        industry=industry, target_platforms=[restricted, "instagram"]
    )
    assert restricted in result.restricted_platforms
    assert restricted not in result.allowed_platforms
    assert len(result.warnings) > 0


# --- Stage 6: generate_hashtags ---

def test_hashtags_contain_topic_token():
    svc = ContentService()
    tags = svc.generate_hashtags(topic="Emergency Plumbing", niche="home-services", research_sources="")
    assert "#emergencyplumbing" in tags.lower().replace(" ", "")


def test_hashtag_fallback_on_error(monkeypatch):
    svc = ContentService()
    monkeypatch.setattr(svc.llm, "generate_hashtags", lambda **kw: (_ for _ in ()).throw(RuntimeError("fail")))
    result = svc.generate_hashtags("t", "n", "")
    assert result == "#content #marketing"


# --- Post shape ---

def test_each_post_has_required_fields():
    result = WorkflowOrchestrator().run_campaign(_request(total_posts=2))
    for post in result["posts"]:
        for field in ("post_type", "platform", "caption", "content", "hashtags", "status"):
            assert field in post


def test_posts_cycle_platforms():
    result = WorkflowOrchestrator().run_campaign(
        _request(total_posts=4, target_platforms=["instagram", "facebook"])
    )
    platforms = [p["platform"] for p in result["posts"]]
    assert "instagram" in platforms
    assert "facebook" in platforms
