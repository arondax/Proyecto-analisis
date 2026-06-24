from pydantic import BaseModel, Field
from typing import Optional

class PrediccionRequest(BaseModel):
    nombre: str = Field(..., example="PlayerName")
    tag: str = Field(..., example="1234")
    region: str = Field(..., example="NA")
    mapa: str = Field(..., example="Ascent")
    es_main: bool = Field(..., example=True)
    num_amigos: int = Field(..., example=5) 
    modelo: Optional[str] = Field("randomforest", description="Modelo a usar: randomforest, arboldeDecision, RegresionLineal")


class PrediccionResponse(BaseModel):
    nombre: str
    mapa: str
    rondas_ganadas: float
    rondas_perdidas: float
    resultado: str
    confianza: Optional[str] = None
    