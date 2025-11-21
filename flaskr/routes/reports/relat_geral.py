from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import RelatGeralForm
from flaskr.db.connection import get_connection
from flask_login import login_required, current_user
from datetime import datetime

relat_geral_bp = Blueprint("relat_geral_bp", __name__)

@relat_geral_bp.route("/relat_geral", methods=["GET", "POST"])
@login_required
def relat_geral():
    form = RelatGeralForm()

    if form.validate_on_submit():
        # Does not get cedente_id from the the form because even 
        # if read-only, can still be manipulated by Dev-Tools
        cedente_id = current_user.id
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")

        return redirect(url_for(
            "reports_bp.relat_geral_bp.relat_geral_result",
            numct=cedente_id,
            dtini=start_date,
            dtfim=end_date
        ))
    
    else:
        if request.method == "POST":
            flash(f"Form invalid: {form.errors}", "danger")

    return render_template("reports/relat_geral.html", form=form)