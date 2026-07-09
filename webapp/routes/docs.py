from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__, url_prefix="/api")


@docs_bp.get("/docs")
def docs():
    return jsonify({
        "endpoints": {
            "GET /api/health": "Health check",
            "GET /api/insights/overview": "Mock analytics overview",
            "POST /api/workflows/campaign": (
                "Run the campaign generation pipeline "
                "(extract_urls → aggregate_research → apply_template → "
                "process_photos → check_restrictions → generate_hashtags → generate_posts)"
            ),
        },
        "notes": "Portfolio-safe surface; all external providers are mocked.",
    })
