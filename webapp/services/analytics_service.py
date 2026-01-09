from typing import Dict


class AnalyticsService:
    def overview(self) -> Dict[str, str]:
        return {
            "status": "mocked",
            "top_channel": "linkedin",
            "engagement_trend": "steady",
            "note": "This data is sample-only for portfolio use.",
        }

    def enrich(self, request: object) -> Dict[str, str]:
        return {
            "audience_fit": "high",
            "channel_priority": "linkedin-first",
            "risk_flag": "none",
        }
