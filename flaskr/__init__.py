from flask import Flask
from flaskr.db.connection import init_pool
from flaskr.routes.auth import auth_bp
from flaskr.routes.menu import menu_bp
from flaskr.routes.reports import reports_bp
from flask_login import LoginManager
from flaskr.models.user_model import User
from config import FlaskConfigs, Cores
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = FlaskConfigs["SECRET_KEY"]
    app.config["SESSION_PERMANENT"] = FlaskConfigs.getboolean("SESSION_PERMANENT")
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)

    init_pool()

    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")


    login_manager = LoginManager()
    login_manager.login_view = "auth_bp.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app
