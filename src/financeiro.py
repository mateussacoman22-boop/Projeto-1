from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Transacao:
    id: int
    tipo: str
    descricao: str
    valor: float
    data: str
    categoria: str


class FinanceDB:
    def __init__(self, db_path: str = "financeiro.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa')),
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL CHECK(valor > 0),
                    data TEXT NOT NULL,
                    categoria TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orcamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
                    ano INTEGER NOT NULL CHECK(ano >= 1900),
                    valor REAL NOT NULL CHECK(valor >= 0),
                    UNIQUE(mes, ano)
                )
                """
            )

    def adicionar_transacao(
        self,
        tipo: str,
        descricao: str,
        valor: float,
        categoria: str,
        data_transacao: Optional[str] = None,
    ) -> int:
        if tipo not in {"receita", "despesa"}:
            raise ValueError("Tipo deve ser 'receita' ou 'despesa'.")
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero.")

        data_transacao = data_transacao or date.today().isoformat()

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO transacoes (tipo, descricao, valor, data, categoria)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tipo, descricao.strip(), valor, data_transacao, categoria.strip()),
            )
            return int(cursor.lastrowid)

    def listar_transacoes(
        self,
        tipo: Optional[str] = None,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
    ) -> Iterable[Transacao]:
        filtros = []
        valores = []

        if tipo:
            filtros.append("tipo = ?")
            valores.append(tipo)
        if mes:
            filtros.append("CAST(strftime('%m', data) AS INTEGER) = ?")
            valores.append(mes)
        if ano:
            filtros.append("CAST(strftime('%Y', data) AS INTEGER) = ?")
            valores.append(ano)

        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        query = f"""
            SELECT id, tipo, descricao, valor, data, categoria
            FROM transacoes
            {where}
            ORDER BY data ASC, id ASC
        """

        with self._connect() as conn:
            rows = conn.execute(query, valores).fetchall()

        return [Transacao(*row) for row in rows]

    def resumo(self, mes: Optional[int] = None, ano: Optional[int] = None) -> dict[str, float]:
        transacoes = self.listar_transacoes(mes=mes, ano=ano)
        receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
        despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
        return {
            "receitas": round(receitas, 2),
            "despesas": round(despesas, 2),
            "saldo": round(receitas - despesas, 2),
        }

    def definir_orcamento(self, mes: int, ano: int, valor: float) -> None:
        if mes < 1 or mes > 12:
            raise ValueError("Mês deve estar entre 1 e 12.")
        if ano < 1900:
            raise ValueError("Ano inválido.")
        if valor < 0:
            raise ValueError("Orçamento não pode ser negativo.")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO orcamentos (mes, ano, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(mes, ano) DO UPDATE SET valor = excluded.valor
                """,
                (mes, ano, valor),
            )

    def consultar_orcamento(self, mes: int, ano: int) -> Optional[float]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT valor FROM orcamentos WHERE mes = ? AND ano = ?",
                (mes, ano),
            ).fetchone()
        return float(row[0]) if row else None
