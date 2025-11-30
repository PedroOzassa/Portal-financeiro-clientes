from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from flaskr.forms import LoginForm
from flaskr.db.connection import get_connection
from flaskr.models.user_model import User
from flask_login import current_user

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/")
@auth_bp.route("/index")
def root():
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for("menu_bp.menu"))

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        remember_me = form.remember_me.data

        query = """
            SELECT CE_NUMCT, CE_RASOC, CE_INTER, CE_DIGDUP, CE_DIGCHE, CE_VENCOLET, CE_SITUA, CE_CGCCE
            FROM DESENPUC.CE_CEDEN
            WHERE CE_LOGII = :Login
              AND CE_SENIN = :Senha
              AND CE_INTER = 'S'
        """

        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {"Login": username, "Senha": password})
                    row = cursor.fetchone()

            if row:
                user = User.from_db_row(row)
                login_user(user, remember=remember_me)  # Flask-Login stores user.id in session
                flash(f"Bem-vindo, {user.rasoc}!", "success")
                return redirect(url_for("menu_bp.menu"))
            else:
                flash("Usuário ou senha inválidos.", "danger")

        except Exception as e:
            flash(f"Erro de conexão: {e}", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_bp.login"))
