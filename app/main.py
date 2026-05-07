from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models
from app.schemas import TransacaoCreate, TransacaoResponse  # importa os schemas do Pydantic
from typing import List  # pra tipar listas

Base.metadata.create_all(bind=engine)  # cria as tabelas no banco se não existirem

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças funcionando!"}

# response_model=TransacaoResponse diz pro FastAPI qual formato retornar
@app.post("/transacoes", response_model=TransacaoResponse)
def criar_transacao(transacao: TransacaoCreate, db: Session = Depends(get_db)):
    # transacao: TransacaoCreate → o Pydantic valida os dados automaticamente
    nova = models.Transacao(**transacao.model_dump())  # converte o schema em modelo do banco
    db.add(nova)      # adiciona no banco
    db.commit()       # salva
    db.refresh(nova)  # atualiza o objeto com os dados do banco (ex: id gerado)
    return nova

# List[TransacaoResponse] → retorna uma lista de transações no formato certo
@app.get("/transacoes", response_model=List[TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).all()  # busca todas as transações

@app.put("/transacoes/{id}", response_model=TransacaoResponse)
def atualizar_transacao(id: int, transacao: TransacaoCreate, db: Session = Depends(get_db)):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == id).first()
    if not db_transacao:
        return {"erro": "Transação não encontrada"}
    for key, value in transacao.model_dump().items():  # atualiza cada campo dinamicamente
        setattr(db_transacao, key, value)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@app.delete("/transacoes/{id}")
def deletar_transacao(id: int, db: Session = Depends(get_db)):
    transacao = db.query(models.Transacao).filter(models.Transacao.id == id).first()
    if not transacao:
        return {"erro": "Transação não encontrada"}
    db.delete(transacao)
    db.commit()
    return {"mensagem": "Transação deletada com sucesso"}

@app.get("/transacoes/tipo/{tipo}", response_model=List[TransacaoResponse])
def filtrar_por_tipo(tipo: str, db: Session = Depends(get_db)):
    # busca apenas transações do tipo informado (receita ou despesa)
    return db.query(models.Transacao).filter(models.Transacao.tipo == tipo).all()

@app.get("/saldo")
def calcular_saldo(db: Session = Depends(get_db)):
    transacoes = db.query(models.Transacao).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
    despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
    saldo = receitas - despesas
    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": saldo
    }