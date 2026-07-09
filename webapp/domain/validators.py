from typing import List

from webapp.models.schema import CampaignRequest


def validate_campaign_request(request: CampaignRequest) -> List[str]:
    issues: List[str] = []
    if not request.topic:
        issues.append("topic is required.")
    if not request.niche:
        issues.append("niche is required.")
    if not request.industry:
        issues.append("industry is required.")
    if not request.target_platforms:
        issues.append("At least one target_platform is required.")
    if request.total_posts < 1:
        issues.append("total_posts must be at least 1.")
    return issues
