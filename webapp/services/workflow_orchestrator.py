from typing import Dict

from webapp.models.schema import CampaignRequest
from webapp.workflows.campaign_workflow import CampaignWorkflow


class WorkflowOrchestrator:
    def __init__(self):
        self.campaign_workflow = CampaignWorkflow()

    def run_campaign(self, request: CampaignRequest) -> Dict[str, object]:
        return self.campaign_workflow.run(request)
