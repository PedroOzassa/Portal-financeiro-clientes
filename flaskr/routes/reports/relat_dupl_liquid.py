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

    if form.validate_on_submit():
        # Does not get cedente_id from the the form because even 
        # if read-only, can still be manipulated by Dev-Tools
        cedente_id = current_user.id
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")

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



@relat_dupl_liquid_bp.route("/relat_dupl_liquid_result")
@login_required
def relat_dupl_liquid_result():
    numct = request.args.get("numct")
    dtini = request.args.get("dtini")
    dtfim = request.args.get("dtfim")

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
                data = [dict(zip(columns, row)) for row in rows]

        total_pago = sum((r["DA_VLPAG"] or 0) for r in data)
        total_titulo = sum((r["DA_VLTIT"] or 0) for r in data)
        now = datetime.now()

        return render_template(
            "reports/relat_dupl_liquid_result.html",
            rows=data,
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
