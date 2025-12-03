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
        cedente_type = current_user.type
        
        # TODO: limit the date interval to the max interval available
        start_date = form.start_date.data.strftime("%d/%m/%Y")
        end_date = form.end_date.data.strftime("%d/%m/%Y")
        
        # Redirects to the result page with the args necessary for the query
        return redirect(url_for(
            "reports_bp.relat_geral_bp.relat_geral_result",
            numct=cedente_id,
            tipcc=cedente_type,
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
    tipcc = request.args.get("tipcc")
    dtini = request.args.get("dtini")
    dtfim = request.args.get("dtfim")

    # Mostly a sanity check. If the form is submitted, it almost surely has data
    if not numct or not tipcc or not dtini or not dtfim:
        flash("Parâmetros de relatório inválidos.", "danger")
        return redirect(url_for("reports_bp.relat_geral_bp.relat_geral"))

    try:
        
        # Gets the latest closing date before the specified date
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        MAX(FC_DTFEC) AS DATAFEC
                    FROM 
                        DESENPUC.FC_FECHA
                    WHERE 
                        FC_DTFEC < TO_DATE(:DtIni, 'DD/MM/YYYY HH24:MI:SS')
                """
                # TODO format all sqls like this
                cursor.execute(query, {"DtIni": dtini})
                row = cursor.fetchone()
                
                datafec = row[0] if row else None # essa data vai ser usada na proxima query
                
        # Uses the date above to get the user's balance on that date
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        SD_SALDO
                    FROM 
                        DESENPUC.SD_SALDO
                    WHERE 
                        SD_TIPCC = :TipCC
                        AND SD_CORRE = :Corre
                        AND SD_DTSLD = :DtIni
                """
                cursor.execute(query, {"TipCC": tipcc, "Corre": numct, "DtIni": datafec})
                row = cursor.fetchone()
                
                sd_saldo = row[0] if row else 0 # Pega 0 pois banco esta errado no momento TODO: pedir para consertar
                
        #TODO: ver se e realmente necessario
        '''
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        CC_SALDO, 
                        CC_DESCR, 
                        DESENPUC.LC_FutCC(CC_TIPCC, CC_CORRE) AS SALDO_FINAL
                    FROM 
                        DESENPUC.CC_CONTC
                    WHERE 
                        CC_TIPCC = :TipCCP 
                        AND CC_CORRE = :CorreP;
                """
                
                cursor.execute(query, {"TipCC": tipcc, "CorreP": numct})
                row = cursor.fetchone()
        '''
                
                
        with get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        TRUNC(LC_DTMOV) AS "Data",
                        LC_HISPA,
                        LC_COHIS,
                        LC_TIPLC AS "Tipo",
                        LC_VLMOV AS VALOR
                    FROM 
                        DESENPUC.LC_LANCC
                    WHERE 
                        LC_TIPCC = :TIPCC
                        AND LC_CORRE = :CORRE
                        AND LC_DTMOV BETWEEN
                            TO_DATE(:DTINI, 'DD/MM/YYYY HH24:MI:SS')
                        AND
                            TO_DATE(:DTFIM, 'DD/MM/YYYY HH24:MI:SS')
                    ORDER BY 
                        LC_DTMOV,
                        LC_DTLAN,
                        LC_TIPLC
                """
                
                cursor.execute(query, {"TIPCC": tipcc, "CORRE": numct, "DTINI": datafec, "DTFIM": dtfim})

                rows = cursor.fetchall()

                columns = ["Data", "LC_HISPA", "LC_COHIS", "Tipo", "VALOR"]
                
                # This creates a list of dicts, one for each table entry received
                table_data = [dict(zip(columns, row)) for row in rows]

        saldo = sd_saldo
        for r in table_data:
            
            valor = r.get("VALOR")

            if r["Tipo"] == "C":
                credito = valor
                debito = ""
                saldo += valor
            else:
                debito = valor
                credito = ""
                saldo -= valor

            r["DEBITO"] = debito
            r["CREDITO"] = credito
            r["SALDO"] = saldo

        now = datetime.now()

        return render_template(
            "reports/relat_geral_result.html",
            numct=numct,
            lancamentos=table_data,
            dtini=datafec.strftime("%d/%m/%Y"),
            dtfim=dtfim,
            rasoc=current_user.rasoc,
            datetime=now
        )

    except Exception as e:
        flash(f"Erro ao gerar relatório: {e}", "danger")
        return redirect(url_for("reports_bp.relat_geral_bp.relat_geral"))
