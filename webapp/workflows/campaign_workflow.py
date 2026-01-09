from dataclasses import asdict
from typing import Dict

from webapp.models.schema import CampaignRequest
from webapp.services.content_service import ContentService
from webapp.services.storage_service import MockStorageService


class CampaignWorkflow:
    def __init__(self):
        self.content_service = ContentService()
        self.storage = MockStorageService()

    def run(self, request: CampaignRequest) -> Dict[str, object]:
        plan = self.content_service.build_plan(request)
        drafts_bundle = self.content_service.generate_drafts(request)
        draft_payload = [asdict(draft) for draft in drafts_bundle["drafts"]]
        storage_result = self.storage.save(
            {"plan": asdict(plan), "drafts": draft_payload}
        )
        return {
            "plan": asdict(plan),
            "drafts": draft_payload,
            "prompt_example": drafts_bundle["prompt"],
            "storage": storage_result,
        }
