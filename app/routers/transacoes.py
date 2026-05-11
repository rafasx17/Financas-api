from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, time

from app.database import get_db
from app import models
from app.schemas import TipoTransacao, TransacaoCreate, TransacaoResponse
from app.auth import get_usuario_atual

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.post("", response_model=TransacaoResponse)
def criar_transacao(
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    nova = models.Transacao(**transacao.model_dump(), usuario_id=usuario.id)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.get("", response_model=List[TransacaoResponse])
def listar_transacoes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).offset(skip).limit(limit).all()


@router.get("/tipo/{tipo}", response_model=List[TransacaoResponse])
def filtrar_por_tipo(
    tipo: TipoTransacao,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id,
        models.Transacao.tipo == tipo
    ).all()


@router.get("/periodo", response_model=List[TransacaoResponse])
def filtrar_por_periodo(
    inicio: date,
    fim: date,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    data_inicio = datetime.combine(inicio, time.min)
    data_fim = datetime.combine(fim, time.max)
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id,
        models.Transacao.criado_em >= data_inicio,
        models.Transacao.criado_em <= data_fim
    ).all()


@router.get("/{id}", response_model=TransacaoResponse)
def buscar_transacao(
    id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao


@router.put("/{id}", response_model=TransacaoResponse)
def atualizar_transacao(
    id: int,
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    db_transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    for key, value in transacao.model_dump().items():
        setattr(db_transacao, key, value)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao


@router.delete("/{id}")
def deletar_transacao(
    id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transacao)
    db.commit()
    return {"mensagem": "Transação deletada com sucesso"}