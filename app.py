from __future__ import annotations

from datetime import date
from flask import Flask, redirect, render_template, request, url_for, flash

from src.financeiro import FinanceDB


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="financeiro-secret-key",
        DB_PATH="financeiro.db",
    )

    if test_config:
        app.config.update(test_config)

    def get_db() -> FinanceDB:
        return FinanceDB(app.config["DB_PATH"])

    @app.get("/")
    def index():
        hoje = date.today()
        db = get_db()
        resumo = db.resumo(mes=hoje.month, ano=hoje.year)
        orcamento = db.consultar_orcamento(mes=hoje.month, ano=hoje.year)
        transacoes = db.listar_transacoes(mes=hoje.month, ano=hoje.year)
        return render_template(
            "index.html",
            mes=hoje.month,
            ano=hoje.year,
            resumo=resumo,
            orcamento=orcamento,
            transacoes=transacoes,
        )

    @app.get("/transacoes")
    def listar_transacoes():
        tipo = request.args.get("tipo") or None
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        db = get_db()
        transacoes = db.listar_transacoes(tipo=tipo, mes=mes, ano=ano)
        resumo = db.resumo(mes=mes, ano=ano)
        return render_template(
            "transacoes.html",
            transacoes=transacoes,
            resumo=resumo,
            filtros={"tipo": tipo, "mes": mes, "ano": ano},
        )

    @app.post("/transacoes")
    def criar_transacao():
        db = get_db()
        try:
            db.adicionar_transacao(
                tipo=request.form["tipo"],
                descricao=request.form["descricao"],
                valor=float(request.form["valor"]),
                categoria=request.form["categoria"],
                data_transacao=request.form.get("data") or None,
            )
            flash("Transação adicionada com sucesso.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("listar_transacoes"))

    @app.get("/orcamento")
    def pagina_orcamento():
        mes = request.args.get("mes", default=date.today().month, type=int)
        ano = request.args.get("ano", default=date.today().year, type=int)
        db = get_db()
        valor = db.consultar_orcamento(mes=mes, ano=ano)
        return render_template("orcamento.html", mes=mes, ano=ano, valor=valor)

    @app.post("/orcamento")
    def salvar_orcamento():
        db = get_db()
        mes = int(request.form["mes"])
        ano = int(request.form["ano"])
        valor = float(request.form["valor"])
        try:
            db.definir_orcamento(mes=mes, ano=ano, valor=valor)
            flash("Orçamento salvo com sucesso.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("pagina_orcamento", mes=mes, ano=ano))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
