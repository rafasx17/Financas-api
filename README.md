# 💰 Finanças API

API REST para gerenciamento de finanças pessoais, desenvolvida com Python e FastAPI.

## 🚀 Tecnologias
- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite

## ⚙️ Como rodar

1. Clone o repositório:

```
git clone https://github.com/rafasx17/Financas-api.git
```

2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Rode a API:

```
uvicorn app.main:app --reload
```

4. Acesse a documentação: http://127.0.0.1:8000/docs

## 📌 Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /transacoes | Lista todas as transações |
| POST | /transacoes | Cria uma nova transação |
| PUT | /transacoes/{id} | Atualiza uma transação |
| DELETE | /transacoes/{id} | Deleta uma transação |