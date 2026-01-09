from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__, url_prefix="/api")


@docs_bp.get("/docs")
def docs():
    return jsonify(
        {
            "endpoints": {
                "GET /api/health": "Health check",
                "GET /api/insights/overview": "Mocked analytics overview",
                "POST /api/workflows/campaign": "Run the mocked campaign workflow",
            },
            "notes": "Portfolio-safe API surface; all providers are mocked.",
        }
    )
