from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models
from app.schemas import TransacaoCreate, TransacaoResponse
from typing import List
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças funcionando!"}

@app.post("/transacoes", response_model=TransacaoResponse)
def criar_transacao(transacao: TransacaoCreate, db: Session = Depends(get_db)):
    nova = models.Transacao(**transacao.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@app.get("/transacoes", response_model=List[TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).all()

@app.get("/transacoes/tipo/{tipo}", response_model=List[TransacaoResponse])
def filtrar_por_tipo(tipo: str, db: Session = Depends(get_db)):
    return db.query(models.Transacao).filter(models.Transacao.tipo == tipo).all()

@app.get("/transacoes/periodo")
def filtrar_por_periodo(inicio: str, fim: str, db: Session = Depends(get_db)):
    data_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    data_fim = datetime.strptime(fim, "%Y-%m-%d")
    return db.query(models.Transacao).filter(
        models.Transacao.criado_em >= data_inicio,
        models.Transacao.criado_em <= data_fim
    ).all()

@app.put("/transacoes/{id}", response_model=TransacaoResponse)
def atualizar_transacao(id: int, transacao: TransacaoCreate, db: Session = Depends(get_db)):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == id).first()
    if not db_transacao:
        return {"erro": "Transação não encontrada"}
    for key, value in transacao.model_dump().items():
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

@app.get("/saldo")
def calcular_saldo(db: Session = Depends(get_db)):
    transacoes = db.query(models.Transacao).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
    despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
    return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}