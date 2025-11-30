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

    # The validate_on_submit() function makes sure all fields comply to
    # the rules set in the forms.py declaration of RelatGeralForm()
    if form.validate_on_submit():
        
        # Does not get cedente_id from the the form because even 
        # if read-only, can still be manipulated by Dev-Tools
        cedente_id = current_user.id
        
        # TODO: get user type
        cedente_type = form.cedente_type.data
        
        # TODO: limit the date interval to the max interval available
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")
        
        # Redirects to the result page with the args necessary for the query
        return redirect(url_for(
            "reports_bp.relat_geral_bp.relat_geral_result",
            numct=cedente_id,
            corre=cedente_type,
            dtini=start_date,
            dtfim=end_date
        ))
    else:
        if request.method == "POST":
            flash(f"Form invalid: {form.errors}", "danger")

    return render_template("reports/relat_geral.html", form=form)

# Made for testing TODO: remove later
@relat_geral_bp.route("/relat_geral_result_test")
@login_required
def relat_geral_result_test():
    return render_template("reports/relat_geral_result.html")

# This address is only accessed if the form is correctly submitted
@relat_geral_bp.route("/relat_geral_result")
@login_required
def relat_geral_result():
    numct = request.args.get("numct")
    corre = request.args.get("corre")
    dtini = request.args.get("dtini")
    dtfim = request.args.get("dtfim")

    # Mostly a sanity check. If the form is submitted, it almost surely has data
    if not numct or not corre or not dtini or not dtfim:
        flash("Parâmetros de relatório inválidos.", "danger")
        return redirect(url_for("reports_bp.relat_geral_bp.relat_geral"))

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT MAX(FC_DTFEC) AS DATAFEC
                    FROM DESENPUC.FC_FECHA
                    WHERE FC_DTFEC < TO_DATE(:DtIni, 'DD/MM/YYYY HH24:MI:SS')
                """
                
                cursor.execute(query, {"DtIni": dtini})
                row = cursor.fetchone()
                
                datafec = row[0] if row else None
                
                
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT SD_SALDO
                    FROM DESENPUC.SD_SALDO
                    WHERE SD_TIPCC = :TipCC
                    AND SD_CORRE = :Corre
                    AND SD_DTSLD = :DtIni
                """
                cursor.execute(query, {"TipCC": numct, "Corre": corre, "DtIni": dtini})
                row = cursor.fetchone()
                
                sd_saldo = row[0] if row else None
                
                
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT MAX(FC_DTFEC) AS DATAFEC
                    FROM DESENPUC.FC_FECHA
                    WHERE FC_DTFEC < TO_DATE(:DtIni, 'DD/MM/YYYY HH24:MI:SS')
                """
                
                cursor.execute(query, {"DtIni": dtini})
                row = cursor.fetchone()
                
                datafec = row[0] if row else None
                
                
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT MAX(FC_DTFEC) AS DATAFEC
                    FROM DESENPUC.FC_FECHA
                    WHERE FC_DTFEC < TO_DATE(:DtIni, 'DD/MM/YYYY HH24:MI:SS')
                """
                
                cursor.execute(query, {"DtIni": dtini})
                row = cursor.fetchone()
                
                datafec = row[0] if row else None
        

        
        now = datetime.now()

        # Passes to the template all arguments to be rendered
        return render_template(
            "reports/relat_geral_result.html",
            datetime=now
        )

    except Exception as e:
        flash(f"Erro ao gerar relatório: {e}", "danger")
        return redirect(url_for("reports_bp.relat_geral_bp.relat_geral"))
