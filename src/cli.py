from __future__ import annotations

import argparse

from src.financeiro import FinanceDB


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sistema de Controle Financeiro")
    parser.add_argument("--db", default="financeiro.db", help="Caminho do arquivo SQLite")

    sub = parser.add_subparsers(dest="comando", required=True)

    adicionar = sub.add_parser("adicionar", help="Adiciona uma nova transação")
    adicionar.add_argument("--tipo", required=True, choices=["receita", "despesa"])
    adicionar.add_argument("--descricao", required=True)
    adicionar.add_argument("--valor", required=True, type=float)
    adicionar.add_argument("--categoria", required=True)
    adicionar.add_argument("--data", help="Data no formato YYYY-MM-DD")

    listar = sub.add_parser("listar", help="Lista transações")
    listar.add_argument("--tipo", choices=["receita", "despesa"])
    listar.add_argument("--mes", type=int)
    listar.add_argument("--ano", type=int)

    resumo = sub.add_parser("resumo", help="Exibe resumo financeiro")
    resumo.add_argument("--mes", type=int)
    resumo.add_argument("--ano", type=int)

    definir_orcamento = sub.add_parser("definir-orcamento", help="Define orçamento mensal")
    definir_orcamento.add_argument("--mes", required=True, type=int)
    definir_orcamento.add_argument("--ano", required=True, type=int)
    definir_orcamento.add_argument("--valor", required=True, type=float)

    orcamento = sub.add_parser("orcamento", help="Consulta orçamento mensal")
    orcamento.add_argument("--mes", required=True, type=int)
    orcamento.add_argument("--ano", required=True, type=int)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    db = FinanceDB(db_path=args.db)

    if args.comando == "adicionar":
        transacao_id = db.adicionar_transacao(
            tipo=args.tipo,
            descricao=args.descricao,
            valor=args.valor,
            categoria=args.categoria,
            data_transacao=args.data,
        )
        print(f"Transação cadastrada com ID {transacao_id}.")

    elif args.comando == "listar":
        transacoes = db.listar_transacoes(tipo=args.tipo, mes=args.mes, ano=args.ano)
        if not transacoes:
            print("Nenhuma transação encontrada.")
            return
        for t in transacoes:
            print(f"[{t.id}] {t.data} | {t.tipo.upper():7} | R$ {t.valor:8.2f} | {t.categoria} | {t.descricao}")

    elif args.comando == "resumo":
        resultado = db.resumo(mes=args.mes, ano=args.ano)
        print(f"Receitas: R$ {resultado['receitas']:.2f}")
        print(f"Despesas: R$ {resultado['despesas']:.2f}")
        print(f"Saldo:    R$ {resultado['saldo']:.2f}")

    elif args.comando == "definir-orcamento":
        db.definir_orcamento(mes=args.mes, ano=args.ano, valor=args.valor)
        print(f"Orçamento definido para {args.mes:02d}/{args.ano}: R$ {args.valor:.2f}")

    elif args.comando == "orcamento":
        valor = db.consultar_orcamento(mes=args.mes, ano=args.ano)
        if valor is None:
            print(f"Nenhum orçamento definido para {args.mes:02d}/{args.ano}.")
        else:
            print(f"Orçamento de {args.mes:02d}/{args.ano}: R$ {valor:.2f}")


if __name__ == "__main__":
    main()
