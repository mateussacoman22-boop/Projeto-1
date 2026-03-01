import os
import tempfile
import unittest

from src.financeiro import FinanceDB


class FinanceDBTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test_financeiro.db")
        self.db = FinanceDB(self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_adicionar_e_listar_transacoes(self) -> None:
        self.db.adicionar_transacao("receita", "Salário", 5000, "Trabalho", "2026-10-01")
        self.db.adicionar_transacao("despesa", "Aluguel", 1800, "Moradia", "2026-10-05")

        transacoes = list(self.db.listar_transacoes())
        self.assertEqual(len(transacoes), 2)
        self.assertEqual(transacoes[0].descricao, "Salário")
        self.assertEqual(transacoes[1].tipo, "despesa")

    def test_resumo_com_filtro_mes_ano(self) -> None:
        self.db.adicionar_transacao("receita", "Salário", 5000, "Trabalho", "2026-10-01")
        self.db.adicionar_transacao("despesa", "Mercado", 900, "Alimentação", "2026-10-08")
        self.db.adicionar_transacao("despesa", "Viagem", 1200, "Lazer", "2026-11-03")

        resumo_outubro = self.db.resumo(mes=10, ano=2026)
        self.assertEqual(resumo_outubro["receitas"], 5000)
        self.assertEqual(resumo_outubro["despesas"], 900)
        self.assertEqual(resumo_outubro["saldo"], 4100)

    def test_orcamento_upsert(self) -> None:
        self.db.definir_orcamento(10, 2026, 3500)
        self.assertEqual(self.db.consultar_orcamento(10, 2026), 3500)

        self.db.definir_orcamento(10, 2026, 4200)
        self.assertEqual(self.db.consultar_orcamento(10, 2026), 4200)

    def test_validacoes(self) -> None:
        with self.assertRaises(ValueError):
            self.db.adicionar_transacao("bonus", "Inválido", 100, "Teste")

        with self.assertRaises(ValueError):
            self.db.adicionar_transacao("receita", "Inválido", 0, "Teste")

        with self.assertRaises(ValueError):
            self.db.definir_orcamento(13, 2026, 100)


if __name__ == "__main__":
    unittest.main()
