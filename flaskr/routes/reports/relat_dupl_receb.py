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
    
    # The validate_on_submit() function makes sure all fields comply to
    # the rules set in the forms.py declaration of RelatDuplRecebForm()
    if form.validate_on_submit():
        
        # Does not get cedente_id from the the form because even 
        # if read-only, can still be manipulated by Dev-Tools
        cedente_id = current_user.id
        situation_filter = form.situation.data
        
        # TODO: limit the date interval to the max interval available
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")

        # Redirects to the result page with the args necessary for the query
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

# This address is only accessed if the form is correctly submitted
@relat_dupl_receb_bp.route("/relat_dupl_receb_result")
@login_required
def relat_dupl_receb_result():
    numct = request.args.get("numct")
    situation = request.args.get("filtr")
    dtini = request.args.get("dtini")
    dtfim = request.args.get("dtfim")

    # Mostly a sanity check. If the form is submitted, it almost surely has data
    if not numct or not situation or not dtini or not dtfim:
        flash("Parâmetros de relatório inválidos.", "danger")
        return redirect(url_for("reports_bp.relat_dupl_receb_bp.relat_dupl_receb"))

    # First table "Posição de Duplicatas a Receber por Cedente"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        DA_DTVEN,
                        DA_VLTIT,
                        DA_DOCUM,
                        DA_PARCE,
                        DA_NUMCT,
                        DA_NUMAC,
                        DA_TIPSA,
                        DA_CGCPF,
                        DA_TIPDA,
                        DA_NROBC,
                        DA_OBSER,
                        DA_CODPO,
                        SA_RASOC,
                        DA_DTPRO,
                        DA_MOTIV,
                        PO_OFICI,
                        DA_NRODV
                    FROM 
                        DESENPUC.DA_DUPAD DA
                        JOIN DESENPUC.SA_SACAD SA
                            ON SA.SA_TIPSA = DA.DA_TIPSA
                           AND SA.SA_CGCPF = DA.DA_CGCPF
                        JOIN DESENPUC.PO_PORTA PO
                            ON PO.PO_CODPO = DA.DA_CODPO
                    WHERE 
                        DA.DA_NUMCT = :NUMCT
                        AND DA.DA_DTPAG IS NULL
                        AND DA.DA_STIMP <> 'N'
                        AND DA.DA_DTVEN BETWEEN :DTINI AND :DTFIM
                        AND (NOT NVL(DA.DA_OBSER, '?') LIKE '%COMPENSA%')
                    ORDER BY 
                        DA.DA_DTVEN, DA.DA_VLTIT, DA.DA_DOCUM, DA.DA_PARCE
                """

                cursor.execute(query, {"NUMCT": numct, "DTINI": dtini, "DTFIM": dtfim})
                rows = cursor.fetchall()

                columns = [
                    "DA_DTVEN", "DA_VLTIT", "DA_DOCUM", "DA_PARCE", "DA_NUMCT",
                    "DA_NUMAC", "DA_TIPSA", "DA_CGCPF", "DA_TIPDA", "DA_NROBC",
                    "DA_OBSER", "DA_CODPO", "SA_RASOC", "DA_DTPRO", "DA_MOTIV",
                    "PO_OFICI", "DA_NRODV"
                ]

                # This creates a list of dicts, one for each table entry received
                first_table_data = [dict(zip(columns, row)) for row in rows]
                # Filters first_table_data based on form option
                
        today = datetime.today().date()
        filtered = []
        for r in first_table_data:
            ven = r["DA_DTVEN"]
            ven_date = ven.date() if hasattr(ven, "date") else ven

            # filtered[] gets not expired entries
            if situation == "1":
                if ven_date >= today:
                    filtered.append(r)

            # filtered[] gets expired entries
            elif situation == "2":
                if ven_date < today:
                    filtered.append(r)

            # filtered[] gets all entries
            elif situation == "3":
                filtered.append(r)

        # Calculates the sum of the DA_VLTIT column
        DA_VLTIT_total = sum((r["DA_VLTIT"] or 0) for r in filtered)
        
        # TODO: move both queries to a single with ... as conn:
        # Second table "Maiores Concentraçôes A RECEBER"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        TIPSA,
                        CGCPF,
                        SA_RASOC,
                        QTDTIT,
                        TOTBRU
                    FROM 
                        DESENPUC.SA_SACAD,
                        (
                            SELECT 
                                TIPSA,
                                CGCPF,
                                QTDTIT,
                                TOTBRU
                            FROM 
                            (
                                SELECT 
                                    DA_TIPSA AS TIPSA,
                                    DA_CGCPF AS CGCPF,
                                    COUNT(*) AS QTDTIT,
                                    SUM(DA_VLTIT) AS TOTBRU
                                FROM 
                                    DESENPUC.AC_ADICT,
                                    DESENPUC.DA_DUPAD
                                WHERE 
                                    DA_NUMCT = :NUMCT
                                    AND DA_DTPAG IS NULL
                                    AND AC_NUMCT = DA_NUMCT
                                    AND AC_NUMAC = DA_NUMAC
                                    AND AC_STIMP <> 'N'
                                GROUP BY 
                                    DA_TIPSA,
                                    DA_CGCPF
                            )
                        )
                    WHERE 
                        SA_TIPSA = TIPSA
                        AND SA_CGCPF = CGCPF
                    ORDER BY 
                        TOTBRU DESC
                """

                cursor.execute(query, {"NUMCT": numct})
                rows = cursor.fetchall()

                columns = [
                    "TIPSA", "CGCPF", "SA_RASOC", "QTDTIT", "TOTBRU"
                ]

                # This creates a list of dicts, one for each table entry received
                second_table_data = [dict(zip(columns, row)) for row in rows]
                
        # Calculates the sum of the TOTBRU column, used to calculate PORCTG
        TOTBRU_total = sum((r["TOTBRU"] or 0) for r in second_table_data)
        
        for r in second_table_data:
            valor = r["TOTBRU"] or 0
            if TOTBRU_total > 0:
                r["PORCTG"] = round((valor / TOTBRU_total) * 100, 2)
            else:
                r["PORCTG"] = 0
            
        now = datetime.now()
        
        return render_template(
            "reports/relat_dupl_receb_result.html",
            first_table=filtered,
            DA_VLTIT_total=DA_VLTIT_total,
            numct=numct,
            dtini=dtini,
            dtfim=dtfim,
            situation=situation,
            rasoc=current_user.rasoc,
            datetime=now,
            second_table=second_table_data
        )

    except Exception as e:
        flash(f"Erro ao gerar relatório: {e}", "danger")
        return redirect(url_for("reports_bp.relat_dupl_receb_bp.relat_dupl_receb"))
