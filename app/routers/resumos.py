from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from app.database import get_db
from app import models
from app.schemas import TipoTransacao
from app.auth import get_usuario_atual

router = APIRouter(prefix="/resumo", tags=["Resumos"])


@router.get("/mensal")
def resumo_mensal(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).all()

    resumo = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0, "saldo": 0.0})

    for t in transacoes:
        chave = t.criado_em.strftime("%Y-%m")
        if t.tipo == TipoTransacao.receita:
            resumo[chave]["receitas"] += t.valor
        else:
            resumo[chave]["despesas"] += t.valor
        resumo[chave]["saldo"] = resumo[chave]["receitas"] - resumo[chave]["despesas"]

    return dict(sorted(resumo.items()))


@router.get("/categorias")
def resumo_por_categoria(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).all()

    resumo = defaultdict(float)

    for t in transacoes:
        chave = t.categoria or "sem categoria"
        resumo[chave] += t.valor

    return dict(sorted(resumo.items()))


@router.get("/saldo")
def calcular_saldo(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.receita)
    despesas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.despesa)
    return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}