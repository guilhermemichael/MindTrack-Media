# app/__init__.py
from flask import Flask, jsonify, render_template, redirect, request, url_for
from flask_login import current_user
from .extensions import db, migrate, bcrypt, login_manager
from .config import Config
from .utils.validators import ValidationError
from .models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login_page"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.path.startswith("/api/"):
            return jsonify({"error": "Nao autorizado"}), 401
        return redirect(url_for("login_page"))

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
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/login")
    def login_page():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard():
        if not current_user.is_authenticated:
            return redirect(url_for("login_page"))
        return render_template("dashboard.html")

    return app
