from flask import Flask
from flaskr.db.connection import init_pool
from flaskr.routes.auth import auth_bp
from flask_login import LoginManager
from flaskr.models.user_model import User
from config import FlaskCfg

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = FlaskCfg["SECRET_KEY"]
    app.config["SESSION_PERMANENT"] = FlaskCfg.getboolean("SESSION_PERMANENT")

    init_pool()

    app.register_blueprint(auth_bp)
    login_manager = LoginManager()
    login_manager.login_view = "auth_bp.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app
