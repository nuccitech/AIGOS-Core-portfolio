from flask import Blueprint, jsonify, request

from webapp.models.schema import CampaignRequest
from webapp.services.workflow_orchestrator import WorkflowOrchestrator


workflows_bp = Blueprint("workflows", __name__, url_prefix="/api/workflows")


@workflows_bp.post("/campaign")
def run_campaign_workflow():
    payload = request.get_json(silent=True) or {}
    campaign_request = CampaignRequest.from_dict(payload)
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run_campaign(campaign_request)
    return jsonify(result)
