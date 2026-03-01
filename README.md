# Sistema de Controle Financeiro (Flask)

Aplicação web completa em Python + Flask para controle financeiro pessoal, com persistência em SQLite.

## Funcionalidades

- Cadastro de receitas e despesas (descrição, valor e categoria), com **data automática do dia atual**.
- Dashboard com resumo do mês atual (receitas, despesas e saldo).
- Listagem e filtro de transações por tipo, mês e ano.
- Definição e consulta de orçamento mensal.

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Instalação

```bash
pip install -r requirements.txt
```

## Executar no Linux/macOS

```bash
python -m flask --app app run --host=0.0.0.0 --port=5000
```

## Executar no Windows (.bat)

Basta dar duplo clique em `run_financeiro.bat` ou executar no terminal:

```bat
run_financeiro.bat
```

Acesse: `http://localhost:5000`

## Testes

```bash
python -m unittest discover -s tests -v
```
