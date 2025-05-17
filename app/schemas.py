from pydantic import BaseModel
from datetime import datetime

# Schemas para SiteBloqueado
class SiteBloqueadoBase(BaseModel):
    url: str
    tipo: str = "apostas"

class SiteBloqueadoCreate(SiteBloqueadoBase):
    pass

class SiteBloqueadoResponse(SiteBloqueadoBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

# Schemas para TentativaAcesso
class TentativaAcessoBase(BaseModel):
    url: str
    usuario_id: str

class TentativaAcessoCreate(TentativaAcessoBase):
    pass

class TentativaAcessoResponse(TentativaAcessoBase):
    id: int
    data_hora: datetime

    class Config:
        orm_mode = True
