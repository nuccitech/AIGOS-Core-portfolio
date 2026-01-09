from flask import Flask

from webapp.config.base import Config
from webapp.routes.docs import docs_bp
from webapp.routes.health import health_bp
from webapp.routes.workflows import workflows_bp
from webapp.routes.insights import insights_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    app.register_blueprint(health_bp)
    app.register_blueprint(workflows_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(docs_bp)

    return app
