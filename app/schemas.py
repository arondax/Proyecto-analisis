from pydantic import BaseModel, Field
from typing import Optional, List

class PrediccionRequest(BaseModel):
    nombre: str = Field(..., example="PlayerName")
    tag: str = Field(..., example="1234")
    region: str = Field(..., example="NA")
    mapa: str = Field(..., example="Ascent")
    es_main: float = Field(..., example=True)
    num_amigos: int = Field(..., example=5) 
    modelo: Optional[str] = Field("randomforest", description="Modelo a usar: randomforest, arboldeDecision, RegresionLineal")


class PrediccionResponse(BaseModel):
    nombre: str
    mapa: str
    rondas_ganadas: float
    rondas_perdidas: float
    resultado: str
    confianza: Optional[str] = None
    
class StatsMapa(BaseModel):
    mapa: str
    partidas: int
    winrate: float
    media_acs: float
    media_kills: float

class EstadisticasResponse(BaseModel):
    nombre: str
    total_partidas: int
    winrate: float
    media_kills: float
    media_muertes: float
    media_acs: float
    media_headshots: float
    mejor_mapa: Optional[str]
    peor_mapa: Optional[str]
    agente_mas_jugado: Optional[str]
    stats_por_mapa: List[StatsMapa]
    
class StatsGrupo (BaseModel):
    categoria: str
    partidas: int
    winrate: float
    media_acs: float
    media_kills: float
    media_muertes: float
    
class CorrelacionItem(BaseModel):
    feature: str
    correlacion: float

class EstadisticasGlobalesResponse(BaseModel):
    total_partidas: int
    por_mapa: List[StatsGrupo]
    por_rango: List[StatsGrupo]
    por_num_amigos: List[StatsGrupo]
    main_vs_no_main: List[StatsGrupo]
    correlacion: List[CorrelacionItem]
    