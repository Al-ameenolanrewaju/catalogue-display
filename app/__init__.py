import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.blueprints.public.routes import public_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.api.routes import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Exempt api blueprint from csrf if desired or needed for json requests
    csrf.exempt(api_bp)

    # Custom error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('public/error.html', error_code=404, message="The page or website showcase you are looking for could not be found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('public/error.html', error_code=500, message="An internal server error occurred. Our engineers have been alerted."), 500

    # Context processors for template formatting
    @app.template_filter('currency')
    def currency_filter(amount):
        if amount is None or amount == 0:
            return "Custom Quote"
        return f"₦{amount:,.0f}"

    return app
