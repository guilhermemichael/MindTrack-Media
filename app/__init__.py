# app/__init__.py
from flask import Flask, jsonify, render_template
from .extensions import db, migrate, bcrypt
from .config import Config
from .utils.validators import ValidationError

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from .routes.auth import bp as auth_bp
    from .routes.media import bp as media_bp
    from .routes.analytics import bp as analytics_bp
    from .routes.upload import bp as upload_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(media_bp, url_prefix="/api/media")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")

    # Error handlers
    @app.errorhandler(ValidationError)
    def handle_val(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Requisição inválida"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Não autorizado"}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Rota não encontrada"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Erro interno do servidor"}), 500

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    return app