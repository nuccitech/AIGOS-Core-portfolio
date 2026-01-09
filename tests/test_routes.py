from webapp import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_workflow_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.post(
        "/api/workflows/campaign",
        json={
            "audience": "product leads",
            "channel_mix": ["linkedin", "email"],
            "goal": "demo requests",
            "tone": "direct",
        },
    )
    assert response.status_code == 200
    assert "plan" in response.json


def test_docs_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "endpoints" in response.json
