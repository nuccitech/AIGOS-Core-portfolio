from webapp import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_workflow_endpoint_returns_200_and_posts():
    app = create_app()
    client = app.test_client()
    response = client.post(
        "/api/workflows/campaign",
        json={
            "topic": "Emergency Plumbing",
            "niche": "home-services",
            "industry": "plumbing",
            "target_platforms": ["instagram", "facebook"],
            "total_posts": 2,
        },
    )
    assert response.status_code == 200
    data = response.json
    assert "posts" in data
    assert "hashtags" in data
    assert "platform_restrictions" in data
    assert "trace" in data


def test_workflow_endpoint_returns_400_on_missing_fields():
    app = create_app()
    client = app.test_client()
    response = client.post(
        "/api/workflows/campaign",
        json={"topic": "", "niche": "", "industry": ""},
    )
    assert response.status_code == 400
    assert "validation_errors" in response.json.get("details", {})


def test_docs_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "endpoints" in response.json
