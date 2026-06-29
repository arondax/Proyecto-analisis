from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
import config

router = APIRouter()

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

@router.get("/estadisticas/{nombre}", response_model=EstadisticasResponse)
def estadisticas(nombre: str):
    ruta = os.path.join(config.DATASET_DIR, f"dataset_{nombre}.csv")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail=f"No hay datos para '{nombre}'")

    df = pd.read_csv(ruta)

    # Filtrar solo competitivo
    df = df[df['modo'].str.lower().isin(['competitive', 'premier'])]
    if df.empty:
        raise HTTPException(status_code=422, detail=f"No hay partidas competitivas para '{nombre}'")

    df['victoria'] = df['rondas_ganadas'] > df['rondas_perdidas']
    df['acs'] = pd.to_numeric(df['acs'], errors='coerce')
    df['headshots'] = pd.to_numeric(df['headshots'], errors='coerce')

    total = len(df)
    winrate = round(df['victoria'].mean() * 100, 1)
    media_kills = round(df['kills'].mean(), 2)
    media_muertes = round(df['muertes'].mean(), 2)
    media_acs = round(df['acs'].mean(), 2)
    df['hs_pct'] = df.apply(
    lambda r: r['headshots'] / r['kills'] if r['kills'] > 0 else 0, axis=1
    )
    media_headshots = round(df['hs_pct'].mean(), 4)
    agente_mas_jugado = df['personaje'].mode().iloc[0] if not df['personaje'].empty else None

    # Stats por mapa
    stats_por_mapa = []
    for mapa, grupo in df.groupby('mapa'):
        stats_por_mapa.append(StatsMapa(
            mapa=mapa,
            partidas=len(grupo),
            winrate=round(grupo['victoria'].mean() * 100, 1),
            media_acs=round(grupo['acs'].mean(), 2),
            media_kills=round(grupo['kills'].mean(), 2),
        ))

    stats_por_mapa.sort(key=lambda x: x.partidas, reverse=True)

    mapas_con_minimo = [s for s in stats_por_mapa if s.partidas >= 3]
    mejor_mapa = max(mapas_con_minimo, key=lambda x: x.winrate).mapa if mapas_con_minimo else None
    peor_mapa = min(mapas_con_minimo, key=lambda x: x.winrate).mapa if mapas_con_minimo else None

    return EstadisticasResponse(
        nombre=nombre,
        total_partidas=total,
        winrate=winrate,
        media_kills=media_kills,
        media_muertes=media_muertes,
        media_acs=media_acs,
        media_headshots=media_headshots,
        mejor_mapa=mejor_mapa,
        peor_mapa=peor_mapa,
        agente_mas_jugado=agente_mas_jugado,
        stats_por_mapa=stats_por_mapa,
    )