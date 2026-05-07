from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransacaoCreate(BaseModel):
    descricao: str
    valor: float
    tipo: str
    categoria: Optional[str] = None  # opcional, não precisa preencher

class TransacaoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str
    categoria: Optional[str] = None
    criado_em: datetime

    class Config:
        from_attributes = True  # permite criar o schema a partir do modelo do banco (SQLAlchemy) usando os atributos do modelo