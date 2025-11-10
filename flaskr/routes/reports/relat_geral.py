from flask import Blueprint, render_template, request, flash
from flask_login import login_required

relat_geral_bp = Blueprint("relat_geral_bp", __name__)

@relat_geral_bp.route("/relat_geral", methods=["GET", "POST"])
@login_required
def relat_geral():
    if request.method == "POST":
        num_cedente = request.form.get("num_cedente")
        tipo_cedente = request.form.get("tipo_cedente")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        interval = request.form.get("interval")

        # temporary for debugging
        print({
            "num_cedente": num_cedente,
            "tipo_cedente": tipo_cedente,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval
        })

        flash("Form submitted successfully!", "success")

    return render_template("reports/relat_geral.html")
