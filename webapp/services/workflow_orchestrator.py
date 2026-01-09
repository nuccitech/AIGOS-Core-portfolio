from typing import Dict

from webapp.config.feature_flags import FeatureFlags
from webapp.container import build_container
from webapp.models.schema import CampaignRequest
from webapp.workflows.campaign_workflow import CampaignWorkflow


class WorkflowOrchestrator:
    def __init__(self):
        container = build_container()
        self.campaign_workflow = CampaignWorkflow(
            container=container,
            enable_insights=FeatureFlags.ENABLE_INSIGHTS,
            enable_persistence=FeatureFlags.ENABLE_PERSISTENCE,
        )

    def run_campaign(self, request: CampaignRequest) -> Dict[str, object]:
        return self.campaign_workflow.run(request)
