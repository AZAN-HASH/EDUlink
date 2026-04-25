import os

from flask import Flask, jsonify, send_from_directory

from config import Config
from .extensions import bcrypt, cors, db, jwt, socketio


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config["IS_PRODUCTION"]:
        if app.config["SECRET_KEY"] == "dev-secret-key-please-change-this-32chars":
            raise RuntimeError("SECRET_KEY must be set for production.")
        if app.config["JWT_SECRET_KEY"] == "dev-jwt-secret-key-please-change-this":
            raise RuntimeError("JWT_SECRET_KEY must be set for production.")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins=app.config["SOCKET_CORS_ORIGINS"])

    from .models import TokenBlocklist
    from .routes import register_blueprints
    from .socket_events import register_socket_events

    @jwt.token_in_blocklist_loader
    def is_token_revoked(_jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"message": "Token has been revoked."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(message):
        return jsonify({"message": message}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(message):
        return jsonify({"message": message}), 422

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "Resource not found."}), 404

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"message": "Uploaded file exceeds the 10MB size limit."}), 413

    @app.errorhandler(500)
    def internal_server_error(_error):
        return jsonify({"message": "Internal server error."}), 500

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    register_blueprints(app)
    register_socket_events()

    with app.app_context():
        db.create_all()

    return app
