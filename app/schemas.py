from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransacaoCreate(BaseModel):
    descricao: str
    valor: float
    tipo: str
    categoria: Optional[str] = None

class TransacaoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str
    categoria: Optional[str] = None
    criado_em: datetime

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str