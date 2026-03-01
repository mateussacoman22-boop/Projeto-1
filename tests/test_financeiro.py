import os
import tempfile
import unittest

try:
    from app import create_app
    FLASK_AVAILABLE = True
except ModuleNotFoundError:
    create_app = None
    FLASK_AVAILABLE = False

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

    def test_resumo_e_orcamento(self) -> None:
        self.db.adicionar_transacao("receita", "Salário", 5000, "Trabalho", "2026-10-01")
        self.db.adicionar_transacao("despesa", "Mercado", 900, "Alimentação", "2026-10-08")
        self.db.definir_orcamento(10, 2026, 3500)

        resumo_outubro = self.db.resumo(mes=10, ano=2026)
        self.assertEqual(resumo_outubro["saldo"], 4100)
        self.assertEqual(self.db.consultar_orcamento(10, 2026), 3500)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask não está instalado no ambiente")
class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test_web.db")
        self.app = create_app({"TESTING": True, "DB_PATH": self.db_path, "SECRET_KEY": "test"})
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_dashboard_carrega(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Controle Financeiro", response.get_data(as_text=True))

    def test_criar_transacao_via_post(self) -> None:
        response = self.client.post(
            "/transacoes",
            data={
                "tipo": "receita",
                "descricao": "Freela",
                "valor": "1200",
                "categoria": "Trabalho",
                            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Transação adicionada com sucesso (data automática de hoje).", response.get_data(as_text=True))

        db = FinanceDB(self.db_path)
        transacoes = list(db.listar_transacoes())
        self.assertEqual(len(transacoes), 1)
        self.assertEqual(transacoes[0].descricao, "Freela")


if __name__ == "__main__":
    unittest.main()
