from typing import List

from webapp.models.schema import CampaignRequest


def validate_campaign_request(request: CampaignRequest) -> List[str]:
    issues: List[str] = []
    if not request.audience:
        issues.append("Audience is required.")
    if not request.channel_mix:
        issues.append("At least one channel is required.")
    if not request.goal:
        issues.append("Goal is required.")
    if not request.tone:
        issues.append("Tone is required.")
    return issues
