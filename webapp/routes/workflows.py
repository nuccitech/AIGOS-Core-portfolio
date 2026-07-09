from flask import Blueprint, jsonify, request

from webapp.models.schema import CampaignRequest
from webapp.services.workflow_orchestrator import WorkflowOrchestrator
from webapp.utils.logger import build_logger


workflows_bp = Blueprint("workflows", __name__, url_prefix="/api/workflows")
logger = build_logger("workflows")


@workflows_bp.post("/campaign")
def run_campaign_workflow():
    payload = request.get_json(silent=True) or {}
    campaign_request = CampaignRequest.from_dict(payload)
    orchestrator = WorkflowOrchestrator()
    try:
        result = orchestrator.run_campaign(campaign_request)
    except ValueError as exc:
        logger.info("validation_failed")
        return jsonify({"error": "validation_failed", "details": exc.args[0]}), 400
    return jsonify(result)
