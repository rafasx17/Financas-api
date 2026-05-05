from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças funcionando!"}

@app.post("/transacoes")
def criar_transacao(descricao: str, valor: float, tipo: str, db: Session = Depends(get_db)):
    transacao = models.Transacao(descricao=descricao, valor=valor, tipo=tipo)
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return transacao

@app.get("/transacoes")
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).all()

@app.put("/transacoes/{id}")
def atualizar_transacao(id: int, descricao: str, valor: float, tipo: str, db: Session = Depends(get_db)):
    transacao = db.query(models.Transacao).filter(models.Transacao.id == id).first()
    if not transacao:
        return {"erro": "Transação não encontrada"}
    transacao.descricao = descricao
    transacao.valor = valor
    transacao.tipo = tipo
    db.commit()
    db.refresh(transacao)
    return transacao

@app.delete("/transacoes/{id}")
def deletar_transacao(id: int, db: Session = Depends(get_db)):
    transacao = db.query(models.Transacao).filter(models.Transacao.id == id).first()
    if not transacao:
        return {"erro": "Transação não encontrada"}
    db.delete(transacao)
    db.commit()
    return {"mensagem": "Transação deletada com sucesso"}