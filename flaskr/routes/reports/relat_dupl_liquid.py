from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import RelatDuplLiquidForm
from flaskr.db.connection import get_connection
from flask_login import login_required, current_user
from datetime import datetime

relat_dupl_liquid_bp = Blueprint("relat_dupl_liquid_bp", __name__)

@relat_dupl_liquid_bp.route("/relat_dupl_liquid", methods=["GET", "POST"])
@login_required
def relat_dupl_liquid():
    form = RelatDuplLiquidForm()

    # The validate_on_submit() function makes sure all fields comply to
    # the rules set in the forms.py declaration of RelatDuplLiquidForm()
    if form.validate_on_submit():
        
        # Does not get cedente_id from the the form because even 
        # if read-only, can still be manipulated by Dev-Tools
        cedente_id = current_user.id
        
        # TODO: limit the date interval to the max interval available
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")

        # Redirects to the result page with the args necessary for the query
        return redirect(url_for(
            "reports_bp.relat_dupl_liquid_bp.relat_dupl_liquid_result",
            numct=cedente_id,
            dtini=start_date,
            dtfim=end_date
        ))
    else:
        if request.method == "POST":
            flash(f"Form invalid: {form.errors}", "danger")

    return render_template("reports/relat_dupl_liquid.html", form=form)


# This address is only accessed if the form is correctly submitted
@relat_dupl_liquid_bp.route("/relat_dupl_liquid_result")
@login_required
def relat_dupl_liquid_result():
    numct = request.args.get("numct")
    dtini = request.args.get("dtini")
    dtfim = request.args.get("dtfim")

    # Mostly a sanity check. If the form is submitted, it almost surely has data
    if not numct or not dtini or not dtfim:
        flash("Parâmetros de relatório inválidos.", "danger")
        return redirect(url_for("reports_bp.relat_dupl_liquid_bp.relat_dupl_liquid"))

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        DA_NUMAC,
                        DA_NUMCT,
                        DA_TIPSA,
                        DA_DOCUM,
                        DA_CGCPF,
                        DA_PARCE,
                        TRUNC(DA_DTPAG) AS DATAPAGTO,
                        DA_DTVEN,
                        DA_VLTIT,
                        SA_RASOC,
                        DA_VLPAG,
                        DA_OBSER,
                        DA_MOTIV
                    FROM 
                        DESENPUC.DA_DUPAD DA
                        JOIN DESENPUC.AC_ADICT AC 
                            ON AC.AC_NUMCT = DA.DA_NUMCT AND AC.AC_NUMAC = DA.DA_NUMAC
                        JOIN DESENPUC.SA_SACAD SA 
                            ON SA.SA_TIPSA = DA.DA_TIPSA AND SA.SA_CGCPF = DA.DA_CGCPF
                    WHERE 
                        DA.DA_NUMCT = :NUMCT
                        AND (
                            (DA.DA_DTPAG BETWEEN 
                                TO_DATE(:DTINI || ' 00:00:00', 'DD/MM/YYYY HH24:MI:SS') 
                                AND TO_DATE(:DTFIM || ' 23:59:59', 'DD/MM/YYYY HH24:MI:SS'))
                            OR (
                                NVL(DA.DA_OBSER, '?') LIKE '%COMPENSA%' 
                                AND DA.DA_DTPAG IS NULL
                            )
                        )
                        AND AC.AC_STIMP = 'S'
                        AND AC.AC_SITUA = 'N'
                    ORDER BY 
                        DA.DA_DTVEN,
                        DA.DA_DOCUM,
                        DA.DA_PARCE
                """
                cursor.execute(query, {"NUMCT": numct, "DTINI": dtini, "DTFIM": dtfim})
                rows = cursor.fetchall()

                columns = [
                    "DA_NUMAC", "DA_NUMCT", "DA_TIPSA", "DA_DOCUM", "DA_CGCPF",
                    "DA_PARCE", "DATAPAGTO", "DA_DTVEN", "DA_VLTIT", "SA_RASOC",
                    "DA_VLPAG", "DA_OBSER", "DA_MOTIV"
                ]
                
                # This creates a list of dicts, one for each table entry received
                table_data = [dict(zip(columns, row)) for row in rows]

        # Calculates the number of late days
        today = datetime.today().date()
        for r in table_data:
            r["ATRASO"] = ""

            ven = r.get("DA_DTVEN")
            pag = r.get("DATAPAGTO")

            if ven and not pag:
                ven_date = ven.date() if hasattr(ven, "date") else ven

                atraso = (today - ven_date).days
                if atraso > 0:
                    r["ATRASO"] = atraso
            else:
                r["ATRASO"] = "0"

        # Calculates the sum of the DA_VLPAG and DA_VLTIT columns
        total_pago = sum((r["DA_VLPAG"] or 0) for r in table_data)
        total_titulo = sum((r["DA_VLTIT"] or 0) for r in table_data)
        
        now = datetime.now()

        # Passes to the template all arguments to be rendered
        return render_template(
            "reports/relat_dupl_liquid_result.html",
            rows=table_data,
            total_pago=total_pago,
            total_titulo=total_titulo,
            numct=numct,
            dtini=dtini,
            dtfim=dtfim,
            rasoc=current_user.rasoc,
            datetime=now
        )

    except Exception as e:
        flash(f"Erro ao gerar relatório: {e}", "danger")
        return redirect(url_for("reports_bp.relat_dupl_liquid_bp.relat_dupl_liquid"))
