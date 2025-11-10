from flask import Flask
from config import FlaskCfg

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = FlaskCfg["SECRET_KEY"]
    app.config["SESSION_PERMANENT"] = FlaskCfg.getboolean("SESSION_PERMANENT")

