from pydantic import BaseModel
from datetime import datetime

class TransacaoCreate(BaseModel):
    descricao: str
    valor: float
    tipo: str

class TransacaoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str
    criado_em: datetime

    class Config:
        from_attributes = True