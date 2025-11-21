from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import RelatDuplRecebForm
from flaskr.db.connection import get_connection
from flask_login import login_required, current_user
from datetime import datetime

relat_dupl_receb_bp = Blueprint("relat_dupl_receb_bp", __name__)

@relat_dupl_receb_bp.route("/relat_dupl_receb", methods=["GET", "POST"])
@login_required
def relat_dupl_receb():
    form = RelatDuplRecebForm()

    if form.validate_on_submit():
        cedente_id = current_user.id
        situation_filter = form.situation.data
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")

        return redirect(url_for(
            "reports_bp.relat_dupl_receb_bp.relat_dupl_receb_result",
            numct=cedente_id,
            filtr=situation_filter,
            dtini=start_date,
            dtfim=end_date
        ))
    
    else:
        if request.method == "POST":
            flash(f"Form invalid: {form.errors}", "danger")

    return render_template("reports/relat_dupl_receb.html", form=form)

