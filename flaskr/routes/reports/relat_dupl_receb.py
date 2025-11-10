from flask import Blueprint, render_template, request, flash
from flask_login import login_required

relat_dupl_receb_bp = Blueprint("relat_dupl_receb_bp", __name__)

@relat_dupl_receb_bp.route("/relat_dupl_receb", methods=["GET", "POST"])
@login_required
def relat_dupl_receb():
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

    return render_template("reports/relat_dupl_receb.html")
