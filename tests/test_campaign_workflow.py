from webapp.models.schema import CampaignRequest
from webapp.services.workflow_orchestrator import WorkflowOrchestrator


def test_campaign_workflow_returns_expected_keys():
    request = CampaignRequest(
        audience="founders",
        channel_mix=["linkedin"],
        goal="demand generation",
        tone="concise",
    )
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run_campaign(request)

    assert "plan" in result
    assert "drafts" in result
    assert "insights" in result
    assert "prompt_example" in result
    assert "trace" in result
