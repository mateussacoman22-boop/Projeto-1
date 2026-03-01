# Sistema de Controle Financeiro

Aplicação de linha de comando para registrar receitas e despesas, definir orçamento mensal e acompanhar saldo acumulado.

## Funcionalidades

- Cadastro de transações (`receita` e `despesa`) com descrição, valor, data e categoria.
- Listagem de transações com filtros opcionais por tipo, mês e ano.
- Resumo financeiro com totais de receitas, despesas e saldo.
- Definição e consulta de orçamento mensal.

## Estrutura

- `src/financeiro.py`: lógica de domínio e persistência em SQLite.
- `src/cli.py`: interface de linha de comando.
- `tests/test_financeiro.py`: testes automatizados.

## Como executar

```bash
python -m src.cli --help
```

### Exemplos

```bash
python -m src.cli adicionar --tipo receita --descricao "Salário" --valor 5000 --categoria Trabalho
python -m src.cli adicionar --tipo despesa --descricao "Aluguel" --valor 1800 --categoria Moradia
python -m src.cli listar --mes 10 --ano 2026
python -m src.cli resumo --mes 10 --ano 2026
python -m src.cli definir-orcamento --mes 10 --ano 2026 --valor 3500
python -m src.cli orcamento --mes 10 --ano 2026
```

## Testes

```bash
python -m unittest discover -s tests -v
```
