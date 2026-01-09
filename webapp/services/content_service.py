from typing import Dict, List

from webapp.integrations.ai_client import MockAIClient
from webapp.models.schema import CampaignPlan, CampaignRequest, DraftContent
from webapp.prompts.example_prompts import CAMPAIGN_PROMPT_EXAMPLE


class ContentService:
    def __init__(self):
        self.ai_client = MockAIClient()

    def build_plan(self, request: CampaignRequest) -> CampaignPlan:
        summary = (
            f"Portfolio mock plan for {request.audience} "
            f"across {', '.join(request.channel_mix)}."
        )
        key_messages = [
            "Highlight primary value proposition.",
            "Include a concise CTA.",
            "Reinforce social proof where relevant.",
        ]
        return CampaignPlan(
            summary=summary,
            channels=request.channel_mix,
            key_messages=key_messages,
        )

    def generate_drafts(self, request: CampaignRequest) -> Dict[str, List[DraftContent]]:
        prompt = CAMPAIGN_PROMPT_EXAMPLE.format(
            audience=request.audience,
            channels=", ".join(request.channel_mix),
            goal=request.goal,
            tone=request.tone,
        )
        ai_response = self.ai_client.generate(prompt)
        drafts = [
            DraftContent(channel="linkedin", title="Launch teaser", body=ai_response["messages"][0]),
            DraftContent(channel="email", title="Customer follow-up", body=ai_response["messages"][1]),
        ]
        return {"prompt": ai_response["prompt_used"], "drafts": drafts}
