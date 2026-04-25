from .admin_routes import admin_bp
from .auth_routes import auth_bp
from .chat_routes import chat_bp
from .clubs_routes import clubs_bp
from .dashboard_routes import dashboard_bp
from .notifications_routes import notifications_bp
from .posts_routes import posts_bp
from .schools_routes import schools_bp
from .search_routes import search_bp
from .users_routes import users_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(schools_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
