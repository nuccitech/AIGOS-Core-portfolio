from flask import Blueprint, jsonify

from webapp.services.analytics_service import AnalyticsService


insights_bp = Blueprint("insights", __name__, url_prefix="/api/insights")


@insights_bp.get("/overview")
def overview():
    service = AnalyticsService()
    return jsonify(service.overview())
