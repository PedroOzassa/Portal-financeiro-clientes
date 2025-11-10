from flask import Blueprint, render_template
from flask_login import login_required

menu_bp = Blueprint("menu_bp", __name__)

@menu_bp.route("/menu")
@login_required
def menu():
    return render_template("menu.html")