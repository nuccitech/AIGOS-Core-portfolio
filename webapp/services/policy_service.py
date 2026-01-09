from typing import Dict

from webapp.models.schema import CampaignRequest


class PolicyService:
    def evaluate(self, request: CampaignRequest) -> Dict[str, str]:
        return {
            "status": "approved",
            "reason": "portfolio-safe policy evaluation (mocked)",
        }
