from typing import Dict, List, Protocol

from webapp.models.schema import CampaignPlan, CampaignRequest, DraftContent


class ContentGenerator(Protocol):
    def build_plan(self, request: CampaignRequest) -> CampaignPlan:
        ...

    def generate_drafts(self, request: CampaignRequest) -> Dict[str, object]:
        ...


class AnalyticsProvider(Protocol):
    def overview(self) -> Dict[str, str]:
        ...

    def enrich(self, request: CampaignRequest) -> Dict[str, str]:
        ...


class StorageProvider(Protocol):
    def save(self, item: Dict[str, object]) -> Dict[str, object]:
        ...
